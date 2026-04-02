import logging

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Note

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Note)
def delete_note_files(sender, instance: Note, **kwargs):
    """Remove Note image objects from storage on permanent delete.

    Soft deletes only set `deleted=True` and do not trigger this signal.
    """

    for field_name in ("image", "thumbnail", "audio"):
        field = getattr(instance, field_name, None)
        if not field:
            continue
        if not getattr(field, "name", None):
            continue

        try:
            field.storage.delete(field.name)
        except Exception:
            logger.exception("Failed deleting %s for Note id=%s", field_name, instance.pk)
