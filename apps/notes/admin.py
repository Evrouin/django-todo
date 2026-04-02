from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin for notes."""

    list_display = ["title", "user", "completed", "deleted", "created_at"]
    list_filter = ["completed", "deleted", "created_at"]
    search_fields = ["title", "body", "user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
