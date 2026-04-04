from django.db import migrations, models


def populate_order_ids(apps, schema_editor):
    Note = apps.get_model("notes", "Note")
    for user_id in Note.objects.order_by().values_list("user_id", flat=True).distinct():
        notes = Note.objects.filter(user_id=user_id).order_by("created_at")
        for index, note in enumerate(notes, start=1):
            Note.objects.filter(pk=note.pk).update(order_id=index)


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0005_add_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="order_id",
            field=models.BigIntegerField(default=0),
        ),
        migrations.RunPython(populate_order_ids, migrations.RunPython.noop),
    ]
