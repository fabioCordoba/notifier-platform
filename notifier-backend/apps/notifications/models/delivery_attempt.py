from django.db import models
from apps.core.models import BaseModel
from .notification import Recipient


class DeliveryAttempt(BaseModel):
    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        PUSH = 'PUSH', 'Push'
        WEBSOCKET = 'WEBSOCKET', 'WebSocket'
        INAPP = 'INAPP', 'In-App'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        QUEUED = 'QUEUED', 'Queued'
        PROCESSING = 'PROCESSING', 'Processing'
        SENT = 'SENT', 'Sent'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'
        READ = 'READ', 'Read'
        CANCELLED = 'CANCELLED', 'Cancelled'

    recipient = models.ForeignKey(
        Recipient, on_delete=models.CASCADE, related_name='delivery_attempts'
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    provider = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    provider_message_id = models.CharField(max_length=255, blank=True)
    attempt_number = models.PositiveSmallIntegerField(default=1)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'delivery_attempts'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['recipient', 'channel', 'status']),
            models.Index(fields=['channel', 'status']),
        ]

    def __str__(self):
        return f"{self.channel} → {self.status} ({self.recipient})"
