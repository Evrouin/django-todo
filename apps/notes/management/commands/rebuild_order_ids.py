"""
Management command to rebuild order_id sequences for each user.
Ensures all order_ids are unique sequential values per user.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.notes.models import Note
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Rebuild order_id sequences to ensure uniqueness per user"

    def handle(self, *args, **options):
        users = User.objects.all()
        total_fixed = 0

        for user in users:
            fixed = self._rebuild_user_order_ids(user)
            if fixed > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"User {user.email}: rebuilt {fixed} order_ids")
                )
                total_fixed += fixed

        self.stdout.write(
            self.style.SUCCESS(f"✓ Rebuilt order_ids for {total_fixed} notes across all users")
        )

    @transaction.atomic
    def _rebuild_user_order_ids(self, user):
        """Rebuild order_id sequence for a single user."""
        notes = Note.objects.filter(user=user, deleted=False).order_by("pinned", "order_id", "created_at")

        count = 0
        for index, note in enumerate(notes, start=1):
            if note.order_id != index:
                note.order_id = index
                note.save(update_fields=["order_id"])
                count += 1

        return count
