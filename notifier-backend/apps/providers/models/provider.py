import json
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from apps.core.models import BaseModel


class Provider(BaseModel):
    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        PUSH = 'PUSH', 'Push'

    class Name(models.TextChoices):
        SENDGRID = 'sendgrid', 'SendGrid'
        SMTP = 'smtp', 'SMTP'
        TWILIO = 'twilio', 'Twilio'
        FIREBASE = 'firebase', 'Firebase'
        CHATWOOT = 'chatwoot', 'Chatwoot'

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='providers',
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    name = models.CharField(max_length=50, choices=Name.choices)
    config_encrypted = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'providers'
        unique_together = ('organization', 'channel', 'name')

    def _get_fernet(self):
        return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())

    def set_config(self, config: dict):
        f = self._get_fernet()
        self.config_encrypted = f.encrypt(json.dumps(config).encode()).decode()

    def get_config(self) -> dict:
        f = self._get_fernet()
        return json.loads(f.decrypt(self.config_encrypted.encode()).decode())

    def save(self, *args, **kwargs):
        if self.is_default:
            Provider.objects.filter(
                organization=self.organization,
                channel=self.channel,
                is_default=True,
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.channel}) - {self.organization}"
