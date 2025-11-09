from base.models import BaseModel
from crops.choices import CropGrowthStageChoices
from django.core.validators import MinValueValidator
from django.db import models
from pest_control.choices import ACTION_THRESHOLD_RISK, PEST_STAGE


class Pest(BaseModel):
    name = models.CharField(
        max_length=100
    )

    scientific_name = models.CharField(
        max_length=250
    )

    stage = models.CharField(
        choices=PEST_STAGE.choices,
        max_length=50,
    )

    action_threshold = models.CharField(
        max_length=50
    )

    action_threshold_risk = models.CharField(
        choices=ACTION_THRESHOLD_RISK.choices,
        max_length=50
    )

    crop_growth_stage = models.CharField(
        choices=CropGrowthStageChoices.choices,
        max_length=50,
        default=CropGrowthStageChoices.VEGETATIVE
    )

    cultural = models.CharField()

    cultural_description = models.TextField()

    biological = models.CharField()

    biological_description = models.TextField()

    presence_period = models.FloatField(
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )

    no_of_plants_affected = models.FloatField(
        blank=True,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )

    slug = None
    metadata = None

    def __str__(self):
        return f"{self.name} - {self.scientific_name} ({self.stage})"

    class Meta:
        verbose_name = "Pest"
        verbose_name_plural = "Pests"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
