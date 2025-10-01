from base.models import BaseModel
from crops.choices import SERVERE, GrowthStage
from crops.models.crop_variety import Crop
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class GrowthStage(BaseModel):
    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE,
        related_name="growth_stage_crop"
    )
    growth_stage = models.CharField(
        max_length=60,
        choices=GrowthStage.choices
    )
    severity = models.CharField(
        max_length=60,
        choices=SERVERE.choices,
        default=SERVERE.NONE
    )
    minimum_days = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    maximum_days = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    created_by = models.ForeignKey(
        User,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False
    )
    updated_by = models.ForeignKey(
        User,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False
    )
    slug = None

    def __str__(self):
        return f"{self.crop_variety.crop_type.name}-{self.growth_stage}"

    class Meta:
        verbose_name = "Growth Stage"
        verbose_name_plural = "Growth Stages"
        unique_together = ("crop", "growth_stage")
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
