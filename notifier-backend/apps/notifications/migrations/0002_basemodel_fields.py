import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        # Notification: add is_active
        migrations.AddField(
            model_name="notification",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="notification",
            name="id",
            field=models.UUIDField(
                default=__import__("uuid").uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        # Recipient: add is_active + updated_at
        migrations.AddField(
            model_name="recipient",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="recipient",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="recipient",
            name="id",
            field=models.UUIDField(
                default=__import__("uuid").uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="recipient",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        # DeliveryAttempt: add is_active
        migrations.AddField(
            model_name="deliveryattempt",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="id",
            field=models.UUIDField(
                default=__import__("uuid").uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
