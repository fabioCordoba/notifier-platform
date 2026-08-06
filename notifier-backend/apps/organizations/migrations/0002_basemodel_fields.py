from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
    ]

    operations = [
        # Organization: alter id + created_at
        migrations.AlterField(
            model_name="organization",
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
            model_name="organization",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        # ApiKey: add updated_at + alter id + created_at
        migrations.AddField(
            model_name="apikey",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="apikey",
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
            model_name="apikey",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
