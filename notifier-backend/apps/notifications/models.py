import uuid
from django.db import models


class Notification(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        QUEUED = 'QUEUED', 'Queued'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        PARTIALLY_FAILED = 'PARTIALLY_FAILED', 'Partially Failed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    template = models.ForeignKey(
        'templates.Template',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    template_variables = models.JSONField(default=dict, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    channels = models.JSONField(default=list)
    metadata = models.JSONField(default=dict, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['scheduled_at']),
        ]

    def __str__(self):
        return f"{self.title} [{self.status}]"

    @property
    def total_recipients(self):
        return self.recipients.count()

    @property
    def delivered_count(self):
        return self.recipients.filter(
            delivery_attempts__status=DeliveryAttempt.Status.DELIVERED
        ).distinct().count()


class Recipient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name='recipients'
    )
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    app_user_id = models.CharField(max_length=255, blank=True)
    push_token = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_recipients'

    def __str__(self):
        return self.name or self.email or self.app_user_id or str(self.id)


class DeliveryAttempt(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'delivery_attempts'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['recipient', 'channel', 'status']),
            models.Index(fields=['channel', 'status']),
        ]

    def __str__(self):
        return f"{self.channel} → {self.status} ({self.recipient})"
