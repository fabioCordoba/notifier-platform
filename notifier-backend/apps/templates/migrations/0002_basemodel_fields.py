from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("templates", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="template",
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
            model_name="template",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
