import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, unique=True, default=uuid.uuid4
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    SAVE_DELETED_DATA_TO_FILE = False

    class Meta:
        abstract = True

    def disable(self):
        self.is_active = False
        self.save()
