from django.db import models
from apps.core.models import BaseModel


class AuditLog(BaseModel):
    class Action(models.TextChoices):
        NOTIFICATION_CREATED = 'NOTIFICATION_CREATED', 'Notification Created'
        NOTIFICATION_SENT = 'NOTIFICATION_SENT', 'Notification Sent'
        NOTIFICATION_FAILED = 'NOTIFICATION_FAILED', 'Notification Failed'
        API_KEY_CREATED = 'API_KEY_CREATED', 'API Key Created'
        API_KEY_REVOKED = 'API_KEY_REVOKED', 'API Key Revoked'
        PROVIDER_CONFIGURED = 'PROVIDER_CONFIGURED', 'Provider Configured'
        TEMPLATE_CREATED = 'TEMPLATE_CREATED', 'Template Created'
        TEMPLATE_UPDATED = 'TEMPLATE_UPDATED', 'Template Updated'

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='audit_logs',
    )
    actor_api_key = models.ForeignKey(
        'organizations.ApiKey',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'action']),
            models.Index(fields=['organization', 'created_at']),
        ]

    def __str__(self):
        return f"{self.action} by {self.actor_api_key} at {self.created_at}"
