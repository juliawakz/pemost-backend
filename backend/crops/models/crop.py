from base.models import BaseModel
from crops.models.crop_type import CropType
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Crop(BaseModel):
    crop_type = models.ForeignKey(
        CropType,
        on_delete=models.CASCADE,
        related_name="crops"
    )

    variety = models.CharField(max_length=100, unique=True)

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

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="crops",
        null=True
    )

    slug = None

    class Meta:
        verbose_name = _("Crop")
        verbose_name_plural = _("Crops")
        unique_together = ("variety", "crop_type")
        ordering = ("-created_at",)
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.crop_type.name} - {self.variety}"

    def save(self, *args, **kwargs):
        self.variety = self.variety.title()
        super().save(*args, **kwargs)
