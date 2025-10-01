import datetime

from base.models import BaseModel
from crops.models.crop_variety import CropVariety
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from farms.models.farm import Farm

User = get_user_model()


class Plantation(BaseModel):
    farm = models.ForeignKey(
        Farm,
        on_delete=models.SET_NULL,
        related_name="farm_plantation",
        null=True
    )
    crop_variety = models.ForeignKey(
        CropVariety,
        on_delete=models.SET_NULL,
        related_name="crop_plantation",
        null=True
    )
    transplanting_date = models.DateField()
    notification_end_date = models.DateField(
        blank=True
    )

    slug = None

    class Meta:
        unique_together = ("farm", "crop_variety", "transplanting_date")
        verbose_name = "Plantation"
        verbose_name_plural = "Plantations"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def __str__(self):
        return self.farm.owner.first_name

    def clean(self):
        super().clean()
        # Validate that the transplanting_date is not greater than today
        if self.transplanting_date > datetime.date.today():
            raise ValidationError(
                "Transplanting date cannot be greater than today."
            )

    def save(self, *args, **kwargs):
        self.clean()
        self.notification_end_date = self.transplanting_date +\
            datetime.timedelta(
                days=self.crop_variety.max_maturity_in_days
            )
        super().save(*args, **kwargs)
