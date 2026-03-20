from django.apps import AppConfig


class TodosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.todos"

    def ready(self) -> None:
        from . import signals  # noqa: F401
