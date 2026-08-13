from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0002_basemodel_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(
                choices=[
                    ('sendgrid', 'SendGrid'),
                    ('smtp', 'SMTP'),
                    ('twilio', 'Twilio'),
                    ('firebase', 'Firebase'),
                    ('chatwoot', 'Chatwoot'),
                ],
                max_length=50,
            ),
        ),
    ]
