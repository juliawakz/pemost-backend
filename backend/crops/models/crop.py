from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Crop(BaseModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    created_by = models.ForeignKey(
        User,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL,
        null=True
    )
    updated_by = models.ForeignKey(
        User,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True
    )

    slug = None
    metadata = None

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Crop"
        verbose_name_plural = "Crops"
