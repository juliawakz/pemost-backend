from django.db import models
from base.models import BaseModel
from django.core.validators import MinValueValidator
from pest_control.choices import ACTION_THRESHOLD_RISK, \
    PEST_STAGE
from backend.crops.models.crop_growth_stage import GrowthStage


class Pest(BaseModel):
    pest_type = models.CharField(
        max_length=100
    )

    scientific_name = models.CharField(
        max_length=250
    )

    pest_stage = models.CharField(
        choices=PEST_STAGE.choices,
        max_length=50
    )

    action_threshold = models.CharField(
        max_length=50
    )

    action_threshold_risk = models.CharField(
        choices=ACTION_THRESHOLD_RISK.choices,
        max_length=50
    )

    growth_stage = models.CharField(
        choices=GrowthStage.choices,
        max_length=50
    )

    cultural = models.CharField()

    cultural_description = models.TextField()

    biological = models.CharField()

    biological_description = models.TextField()

    pest_presence_period = models.FloatField(
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
        return f"{self.pest_type}"

    class Meta:
        verbose_name = "Pest"
        verbose_name_plural = "Pests"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
