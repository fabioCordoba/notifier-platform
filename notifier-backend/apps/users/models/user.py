import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    is_org_admin = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True)

    class Meta:
        db_table = 'users'
