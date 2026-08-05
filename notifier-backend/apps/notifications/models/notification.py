from django.db import models
from apps.core.models import BaseModel


class Notification(BaseModel):
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
        from .delivery_attempt import DeliveryAttempt
        return self.recipients.filter(
            delivery_attempts__status=DeliveryAttempt.Status.DELIVERED
        ).distinct().count()


class Recipient(BaseModel):
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name='recipients'
    )
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    app_user_id = models.CharField(max_length=255, blank=True)
    push_token = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'notification_recipients'

    def __str__(self):
        return self.name or self.email or self.app_user_id or str(self.id)
