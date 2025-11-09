import datetime

from base.models import BaseModel
from crops.models.crop_variety import CropVariety
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from app.models.farm import Farm

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
        related_name="crop_variety_plantation",
        null=True
    )
    transplanting_date = models.DateField()
    notification_end_date = models.DateField(
        blank=True,
        null=True
    )
    is_matured = models.BooleanField(
        default=False,
        help_text="Whether the crop has reached maturity"
    )

    slug = None

    class Meta:
        unique_together = ("farm", "crop_variety", "transplanting_date")
        verbose_name = "Plantation"
        verbose_name_plural = "Plantations"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
        indexes = [
            models.Index(fields=['farm', 'is_matured']),
            models.Index(fields=['is_archived', 'is_matured']),
        ]

    def __str__(self):
        if self.farm and self.farm.farmer:
            return f"{self.farm.farmer.full_name} - {self.crop_variety.name if self.crop_variety else 'No Crop'}"
        return f"Plantation {self.id}"

    def clean(self):
        super().clean()
        # Validate that the transplanting_date is not greater than today
        if self.transplanting_date > datetime.date.today():
            raise ValidationError(
                "Transplanting date cannot be greater than today."
            )

        # Check for active plantations only when creating a new plantation
        # (pk is None for new instances)
        if self.pk is None and self.farm:
            from django.db.models import Q
            active_plantation = Plantation.objects.filter(
                Q(farm=self.farm),
                Q(is_matured=False),
                Q(is_archived=False)
            ).first()

            if active_plantation:
                raise ValidationError(
                    f"This farm already has an active plantation "
                    f"({active_plantation.crop_variety.name if active_plantation.crop_variety else 'Unknown crop'}) "
                    f"planted on {active_plantation.transplanting_date}. "
                    f"Please wait until it matures before adding a new plantation."
                )

    def save(self, *args, **kwargs):
        self.clean()
        if self.crop_variety and self.crop_variety.max_maturity_days:
            self.notification_end_date = self.transplanting_date + \
                datetime.timedelta(
                    days=self.crop_variety.max_maturity_days
                )

            # Check if crop has reached maturity
            if datetime.date.today() >= self.notification_end_date:
                self.is_matured = True

        super().save(*args, **kwargs)
