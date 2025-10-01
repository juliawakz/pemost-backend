from base.models import BaseModel
from crops.choices import GrowthStageChoices, SeverityChoices
from crops.models.crop_variety import CropVariety
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class GrowthStage(BaseModel):
    crop_variety = models.ForeignKey(
        CropVariety,
        on_delete=models.CASCADE,
        related_name="%(class)s_growth_stage",
        null=True
    )
    growth_stage = models.CharField(
        max_length=60,
        choices=GrowthStageChoices.choices
    )
    severity = models.CharField(
        max_length=60,
        choices=SeverityChoices.choices,
        default=SeverityChoices.NONE
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
    metadata = None

    def __str__(self):
        return f"{self.crop_variety.crop_type.name}-{self.growth_stage}"

    class Meta:
        verbose_name = "Growth Stage"
        verbose_name_plural = "Growth Stages"
        unique_together = ("crop_variety", "growth_stage")
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
