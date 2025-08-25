import uuid

from base.managers import BaseManager
from django.contrib.gis.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, db_index=True)
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)
    is_archived = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, null=True, blank=True)

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ("-updated_at", "-created_at")
