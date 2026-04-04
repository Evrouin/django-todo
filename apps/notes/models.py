import uuid

from django.conf import settings
from django.db import models


class Note(models.Model):
    """Note item belonging to a user."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="notes/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="notes/thumbs/", blank=True, null=True)
    audio = models.FileField(upload_to="notes/audio/", blank=True, null=True)
    link_previews = models.JSONField(blank=True, default=list)
    completed = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    order_id = models.BigIntegerField(default=0)
    color = models.CharField(max_length=20, default="default")
    reminder_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notes"
        ordering = ["-pinned", "-order_id", "-created_at"]
        indexes = [
            models.Index(fields=["user", "deleted"]),
            models.Index(fields=["user", "-pinned", "-order_id"]),
        ]

    def __str__(self):
        return self.title
