from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes as perm_classes
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note
from .serializers import NoteSerializer


class NotePagination(CursorPagination):
    """Cursor pagination for notes."""

    page_size = 20
    ordering = "-created_at"
    cursor_query_param = "cursor"


class ApiResponseMixin:
    """Mixin to wrap responses in the Nuxt ApiResponse format."""

    def api_response(self, data, status_code=200):
        return Response(
            {"data": data, "statusCode": status_code, "timestamp": timezone.now().isoformat()},
            status=status_code,
        )


@method_decorator(ratelimit(key="user", rate="60/h", method="POST"), name="dispatch")
class NoteListCreateView(ApiResponseMixin, generics.ListCreateAPIView):
    """List and create notes for the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer
    pagination_class = NotePagination

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)  # type: ignore[misc]
        if self.request.query_params.get("deleted_only") == "true":
            queryset = queryset.filter(deleted=True)
        elif self.request.query_params.get("include_deleted") != "true":
            queryset = queryset.filter(deleted=False)
        completed = self.request.query_params.get("completed")
        if completed == "true":
            queryset = queryset.filter(completed=True)
        elif completed == "false":
            queryset = queryset.filter(completed=False)
        return queryset

    @extend_schema(summary="List notes", description="Get all notes for the authenticated user. Pass ?include_deleted=true to include soft-deleted notes.")
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        paginated = self.get_paginated_response(serializer.data)
        return Response(
            {
                "data": serializer.data,
                "next": paginated.data.get("next"),
                "previous": paginated.data.get("previous"),
                "statusCode": 200,
                "timestamp": timezone.now().isoformat(),
            },
        )

    MAX_NOTES_PER_USER = 100

    @extend_schema(summary="Create note", description="Create a new note for the authenticated user.")
    def create(self, request, *args, **kwargs):
        if not settings.DEBUG and Note.objects.filter(user=request.user, deleted=False).count() >= self.MAX_NOTES_PER_USER:
            return self.api_response(
                {"error": f"Note limit reached ({self.MAX_NOTES_PER_USER}). Delete some notes first."},
                status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return self.api_response(serializer.data, status.HTTP_201_CREATED)


class NoteDetailView(ApiResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a single note."""

    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)  # type: ignore[misc]

    @extend_schema(summary="Get note", description="Get a single note by ID.")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.api_response(serializer.data)

    @extend_schema(summary="Update note", description="Full update of a note.")
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.api_response(serializer.data)

    @extend_schema(summary="Partial update note", description="Partial update of a note (e.g., toggle completed).")
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.api_response(serializer.data)

    @extend_schema(summary="Delete note", description="Soft delete on first call, permanent delete if already soft-deleted.")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.deleted:
            instance.delete()
        else:
            instance.deleted = True
            instance.save()
        return self.api_response({"success": True})


@extend_schema(summary="Bulk delete notes", description="Soft delete multiple notes by IDs.")
@api_view(["POST"])
@perm_classes([IsAuthenticated])
def bulk_delete_notes(request):
    """Bulk delete notes. Soft-deletes active notes, permanently deletes already soft-deleted ones."""
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
    notes = Note.objects.filter(id__in=ids, user=request.user)
    permanent_ids = list(notes.filter(deleted=True).values_list("id", flat=True))
    notes.filter(deleted=False).update(deleted=True)
    Note.objects.filter(id__in=permanent_ids).delete()
    return Response({"success": True})


@extend_schema(summary="Bulk pin/unpin notes", description="Pin or unpin multiple notes by IDs.")
@api_view(["POST"])
@perm_classes([IsAuthenticated])
def bulk_pin_notes(request):
    """Bulk pin or unpin notes."""
    ids = request.data.get("ids", [])
    pinned = request.data.get("pinned", True)
    if not ids:
        return Response({"error": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
    Note.objects.filter(id__in=ids, user=request.user).update(pinned=pinned)
    return Response({"success": True})


@extend_schema(summary="Bulk restore notes", description="Restore multiple soft-deleted notes by IDs.")
@api_view(["POST"])
@perm_classes([IsAuthenticated])
def bulk_restore_notes(request):
    """Bulk restore soft-deleted notes."""
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
    Note.objects.filter(id__in=ids, user=request.user, deleted=True).update(deleted=False)
    return Response({"success": True})
