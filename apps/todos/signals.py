import logging

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Todo

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Todo)
def delete_todo_files(sender, instance: Todo, **kwargs):
    """Remove Todo image objects from storage on permanent delete.

    Soft deletes only set `deleted=True` and do not trigger this signal.
    """

    for field_name in ("image", "thumbnail"):
        field = getattr(instance, field_name, None)
        if not field:
            continue
        if not getattr(field, "name", None):
            continue

        try:
            field.storage.delete(field.name)
        except Exception:
            logger.exception("Failed deleting %s for Todo id=%s", field_name, instance.pk)

