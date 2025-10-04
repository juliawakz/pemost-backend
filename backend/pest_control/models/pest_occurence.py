from base.models import BaseModel
from django.contrib.gis.db import models as gis_models


class PestOccurrence(BaseModel):
    yellow_buffer = gis_models.GeometryField(
        null=True,
        srid=4326,
        blank=True
    )

    red_buffer = gis_models.GeometryField(
        null=True,
        srid=4326,
        blank=True
    )

    green_buffer = gis_models.GeometryField(
        null=True,
        srid=4326,
        blank=True
    )

    slug = None
    metadata = None

    class Meta:
        verbose_name = "Occurrence"
        verbose_name_plural = "Occurrences"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
