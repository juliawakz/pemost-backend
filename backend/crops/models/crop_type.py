from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CropType(BaseModel):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="crop_type_owner",
        null=True
    )
    slug = None

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Crop Type"
        verbose_name_plural = "Crop Types"
