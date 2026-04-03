import uuid

from django.db import migrations, models


def populate_uuids(apps, schema_editor):
    User = apps.get_model("users", "User")
    for user in User.objects.filter(uuid__isnull=True):
        user.uuid = uuid.uuid4()
        user.save(update_fields=["uuid"])


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_add_account_lockout"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
