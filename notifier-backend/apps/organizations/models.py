import uuid
import hashlib
import secrets
from django.db import models
from django.utils import timezone


class Organization(models.Model):
    class Plan(models.TextChoices):
        FREE = 'FREE', 'Free'
        STARTER = 'STARTER', 'Starter'
        GROWTH = 'GROWTH', 'Growth'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='org_logos/', null=True, blank=True)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ApiKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='api_keys'
    )
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=128, unique=True)
    key_prefix = models.CharField(max_length=12)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']

    @classmethod
    def generate(cls, organization, name):
        raw_key = f"ntf_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        instance = cls.objects.create(
            organization=organization,
            name=name,
            key_hash=key_hash,
            key_prefix=raw_key[:12],
        )
        return instance, raw_key

    @classmethod
    def authenticate(cls, raw_key):
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            key = cls.objects.select_related('organization').get(
                key_hash=key_hash,
                is_active=True,
                organization__is_active=True,
            )
            if key.expires_at and key.expires_at < timezone.now():
                return None
            key.last_used_at = timezone.now()
            key.save(update_fields=['last_used_at'])
            return key
        except cls.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.key_prefix}... ({self.organization.name})"
