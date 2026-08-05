from django.db import models
from apps.core.models import BaseModel


class Template(BaseModel):
    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        WEBSOCKET = 'WEBSOCKET', 'WebSocket'
        INAPP = 'INAPP', 'In-App'

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='templates',
    )
    name = models.CharField(max_length=255)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    variables = models.JSONField(
        default=list,
        help_text='Lista de nombres de variables esperadas, ej: ["nombre", "codigo"]'
    )

    class Meta:
        db_table = 'templates'
        unique_together = ('organization', 'name', 'channel')
        ordering = ['-created_at']

    def render(self, variables: dict) -> dict:
        rendered_body = self.body
        rendered_subject = self.subject
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered_body = rendered_body.replace(placeholder, str(value))
            rendered_subject = rendered_subject.replace(placeholder, str(value))
        return {'subject': rendered_subject, 'body': rendered_body}

    def __str__(self):
        return f"{self.name} [{self.channel}]"
