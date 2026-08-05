from django.db import models


class HierarchyLevel(models.TextChoices):
    PLATFORM_ADMIN = 'platform_admin', 'Platform Admin'
    ORG_ADMIN = 'org_admin', 'Org Admin'
    SUPERVISOR = 'supervisor', 'Supervisor'
