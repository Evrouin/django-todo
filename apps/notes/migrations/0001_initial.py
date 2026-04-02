from django.conf import settings
from django.db import connection, migrations, models
import django.db.models.deletion


def rename_if_exists(apps, schema_editor):
    """Rename todos→notes if the old table exists (existing deployments only)."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'todos');"
        )
        if cursor.fetchone()[0]:
            cursor.execute("ALTER TABLE todos RENAME TO notes;")
            cursor.execute("DROP INDEX IF EXISTS todos_user_id_4c2949_idx;")
            cursor.execute("DROP INDEX IF EXISTS todos_user_id_d2e0d8_idx;")


def create_if_missing(apps, schema_editor):
    """Create the notes table only if it doesn't already exist (fresh DB)."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notes');"
        )
        if not cursor.fetchone()[0]:
            Note = apps.get_model("notes", "Note")
            schema_editor.create_model(Note)


def reverse(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notes');"
        )
        if cursor.fetchone()[0]:
            cursor.execute("ALTER TABLE notes RENAME TO todos;")


class Migration(migrations.Migration):
    """Rename the old 'todos' table to 'notes', or create fresh on new DBs."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Note",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("title", models.CharField(max_length=255)),
                        ("body", models.TextField(blank=True, default="")),
                        ("image", models.ImageField(blank=True, null=True, upload_to="notes/")),
                        ("thumbnail", models.ImageField(blank=True, null=True, upload_to="notes/thumbs/")),
                        ("completed", models.BooleanField(default=False)),
                        ("deleted", models.BooleanField(default=False)),
                        ("pinned", models.BooleanField(default=False)),
                        ("color", models.CharField(default="default", max_length=20)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notes", to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        "db_table": "notes",
                        "ordering": ["-pinned", "-created_at"],
                        "indexes": [
                            models.Index(fields=["user", "deleted"], name="notes_user_id_9e131c_idx"),
                            models.Index(fields=["user", "-pinned", "-created_at"], name="notes_user_id_429168_idx"),
                        ],
                    },
                ),
            ],
        ),
        migrations.RunPython(rename_if_exists, reverse),
        migrations.RunPython(create_if_missing, migrations.RunPython.noop),
    ]
