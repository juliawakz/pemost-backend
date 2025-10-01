from base.models import BaseModel
from crops.models.crop import Crop
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CropVariety(BaseModel):
    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE,
        related_name="crops"
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    min_maturity_days = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_maturity_days = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    min_yield = models.FloatField(default=0, validators=[MinValueValidator(0)])
    max_yield = models.FloatField(default=0, validators=[MinValueValidator(0)])

    climate = models.CharField(max_length=100)

    min_rainfall_mm = models.FloatField(default=0, validators=[MinValueValidator(0)])
    max_rainfall_mm = models.FloatField(default=0, validators=[MinValueValidator(0)])

    min_altitude_masl = models.FloatField(default=0, validators=[MinValueValidator(0)])
    max_altitude_masl = models.FloatField(default=0, validators=[MinValueValidator(0)])

    row_spacing_cm = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    plant_spacing_hill = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])

    fertilizer_dap_kg = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    fertilizer_can_kg = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    fertilizer_17_17_17_kg = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])

    disease_tolerance = models.TextField(blank=True, null=True)
    pest_tolerance = models.TextField(blank=True, null=True)
    pest_susceptibility = models.TextField(blank=True, null=True)
    disease_susceptibility = models.TextField(blank=True, null=True)

    seed_source = models.TextField(blank=True, null=True)
    seed_rate_g_per_acre = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])

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

    class Meta:
        verbose_name = _("Crop Variety")
        verbose_name_plural = _("Crop Varieties")
        unique_together = ("name", "crop")
        ordering = ("-created_at",)
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)
