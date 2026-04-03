import uuid

from django.db import migrations, models


def populate_uuids(apps, schema_editor):
    Note = apps.get_model("notes", "Note")
    for note in Note.objects.filter(uuid__isnull=True):
        note.uuid = uuid.uuid4()
        note.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0004_add_link_previews"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="note",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
