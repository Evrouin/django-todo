from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.todos.models import Todo
from apps.todos.views import TodoPagination
from apps.users.admin_serializers import AdminCreateUserSerializer, AdminTodoSerializer
from apps.users.permissions import IsSuperUser
from apps.users.serializers import UserSerializer

User = get_user_model()


class AdminUserListView(generics.ListCreateAPIView):
    """List and create users (superuser only)."""

    permission_classes = [IsSuperUser]
    queryset = User.objects.all().order_by("-created_at")
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "username"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminCreateUserSerializer
        return UserSerializer

    @extend_schema(summary="List all users", description="Admin endpoint to list all users.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Create user", description="Admin endpoint to create a new user.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, and delete any user (superuser only)."""

    permission_classes = [IsSuperUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @extend_schema(summary="Get user detail", description="Admin endpoint to get user detail.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Update user", description="Admin endpoint to update a user.")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary="Delete user", description="Admin endpoint to permanently delete a user.")
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({"error": "Cannot delete yourself."}, status=400)
        return super().destroy(request, *args, **kwargs)


class AdminTodoListView(generics.ListAPIView):
    """List all todos across users (superuser only)."""

    permission_classes = [IsSuperUser]
    serializer_class = AdminTodoSerializer
    pagination_class = TodoPagination
    queryset = Todo.objects.select_related("user").all().order_by("-created_at")
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "body", "user__email"]

    @extend_schema(summary="List all todos", description="Admin endpoint to list all todos.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AdminTodoDetailView(generics.RetrieveDestroyAPIView):
    """View and delete any todo (superuser only)."""

    permission_classes = [IsSuperUser]
    serializer_class = AdminTodoSerializer
    queryset = Todo.objects.select_related("user").all()

    @extend_schema(summary="Get todo detail", description="Admin endpoint to view a todo with user info.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Delete todo", description="Admin endpoint to permanently delete a todo.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(summary="Dashboard stats", description="Admin endpoint for dashboard statistics.")
@api_view(["GET"])
@permission_classes([IsSuperUser])
def admin_stats(request):
    """Dashboard statistics."""
    now = timezone.now()
    return Response(
        {
            "users": {
                "total": User.objects.count(),
                "verified": User.objects.filter(is_verified=True).count(),
                "joined_today": User.objects.filter(created_at__date=now.date()).count(),
            },
            "todos": {
                "total": Todo.objects.count(),
                "completed": Todo.objects.filter(completed=True).count(),
                "deleted": Todo.objects.filter(deleted=True).count(),
                "active": Todo.objects.filter(completed=False, deleted=False).count(),
            },
        }
    )
