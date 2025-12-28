import datetime
import math
import os
import re
from datetime import timezone

from app.choices import ACTION_THRESHOLD_RISK, PEST_STAGE, SERVERE, GrowthStage
from base.models import BaseModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def titlecase(s):
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?",
        lambda word: word.group(0).capitalize(),
        s)


def get_spectral_indices_photos_dir(instance, filename):
    """get spectral indices tiffs

    :param instance:
    :param filename: image name

    :return: path to image
    :rtype: str

    """
    f_name, ext = os.path.splitext(filename)
    return os.path.join("spectral_index", str(instance.spectral_index_name), " " + str(timezone.now())[:19] + ext)


class Crop_Type(BaseModel):
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)
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


class Crop_Variety(BaseModel):
    crop_type = models.ForeignKey(Crop_Type, on_delete=models.CASCADE, related_name="crop_variety_crop")
    crop_variety = models.CharField(
        max_length=100, unique=True, blank=False, null=False
    )
    min_maturity_in_days = models.IntegerField(
        blank=False, null=False, default=0, validators=[MinValueValidator(0)]
    )
    max_maturity_in_days = models.IntegerField(
        blank=False, null=False, default=0, validators=[MinValueValidator(0)]
    )
    min_estimated_yield = models.FloatField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    max_estimated_yield = models.FloatField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    suitable_climatic_conditions = models.CharField(
        max_length=100, blank=False, null=False
    )
    min_annual_rainfall_mm = models.FloatField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    max_annual_rainfall_mm = models.FloatField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    min_altitude_meters_above_sea_level = models.FloatField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    max_altitude_meters_above_sea_level = models.FloatField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    row_spacing_cm = models.IntegerField(
        null=False, blank=False, default=0, validators=[MinValueValidator(0)]
    )
    plant_spacing_1_plant_per_hill = models.IntegerField(
        null=False, blank=True, default=0, validators=[MinValueValidator(0)]
    )
    fertilizer_requirements_planting_DAP_kgs = models.IntegerField(
        null=False, blank=True, default=0, validators=[MinValueValidator(0)]
    )
    fertilizer_requirements_topdressing_CAN_kgs = models.IntegerField(
        null=True, blank=True, default=0, validators=[MinValueValidator(0)]
    )
    fertilizer_requirements_topdressing_17_17_kgs = models.IntegerField(
        null=False, blank=True, default=0, validators=[MinValueValidator(0)]
    )
    diseases_tolerance = models.TextField(
        blank=True, null=True
    )
    pest_tolerance = models.TextField(
        blank=True, null=True
    )
    pest_susceptibility = models.TextField(
        blank=True, null=True
    )
    disease_susceptibility = models.TextField(
        blank=True, null=True
    )
    seed_source = models.TextField(
        blank=True, null=True
    )
    Seed_rate_per_acre_grams = models.IntegerField(
        null=True, blank=True, default=0, validators=[MinValueValidator(0)]
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="crop_variety_owner",
        null=True
    )
    slug = None

    class Meta:
        verbose_name = _("Crop Variety")
        verbose_name_plural = _("Crop Varieties")
        unique_together = ("crop_type", "crop_variety")
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def __str__(self):
        return f"{self.crop_type.name}-{self.crop_variety}"

    def save(self, *args, **kwargs):
        self.crop_variety = self.crop_variety.title()
        super().save(*args, **kwargs)


class Growth_Stage(BaseModel):
    crop_variety = models.ForeignKey(Crop_Variety, on_delete=models.CASCADE, related_name="growth_stage_crop")
    growth_stage = models.CharField(max_length=60, choices=GrowthStage.choices)
    severity = models.CharField(max_length=60, choices=SERVERE.choices, default=SERVERE.NONE)
    minimum_days = models.IntegerField(validators=[MinValueValidator(0)])
    maximum_days = models.IntegerField(validators=[MinValueValidator(0)])
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="growth_stage_owner",
        null=True
    )
    slug = None

    def __str__(self):
        return f"{self.crop_variety.crop_type.name}-{self.growth_stage}"

    class Meta:
        verbose_name = "Growth Stage"
        verbose_name_plural = "Growth Stages"
        unique_together = ("crop_variety", "growth_stage")
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)


class County(BaseModel):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    county_num = models.IntegerField(
        blank=False,
        unique=True,
        null=False,
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(47)],
    )
    slug = None

    def __str__(self):
        return f"{self.name}-{self.county_num}"

    class Meta:
        verbose_name = "County"
        verbose_name_plural = "Counties"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def save(self, *args, **kwargs):
        self.name = titlecase(self.name)
        return super().save(*args, **kwargs)


class SubCounty(BaseModel):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    county = models.ForeignKey(
        County, related_name="county_subcounty", on_delete=models.CASCADE
    )
    slug = None

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "SubCounty"
        verbose_name_plural = "SubCounties"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        return super().save(*args, **kwargs)


class Ward(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    subcounty = models.ForeignKey(
        SubCounty, related_name="subcounty_ward", on_delete=models.CASCADE
    )
    slug = None

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Ward"
        verbose_name_plural = "Wards"
        unique_together = ("name", "subcounty")
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        return super().save(*args, **kwargs)


def get_sqm_by_wgs84_polygon(geom):
    """
    Converts wgs 84 coordinates(lat/lon) to projected coordinates(meters) and get the acreage of a farm
    :param geom:
    :return: area
    """

    def get_utm_by_wgs_84(cent_lon, cent_lat):
        utm_zone_num = int(math.floor((cent_lon + 180) / 6) + 1)
        utm_zone_hemi = 6 if cent_lat >= 0 else 7
        utm_epsg = 32000 + utm_zone_hemi * 100 + utm_zone_num
        return utm_epsg

    lon = geom.centroid.x
    lat = geom.centroid.y
    epsg_code = get_utm_by_wgs_84(lon, lat)

    transformed_geom = geom.transform(epsg_code, clone=True)
    area = transformed_geom.area * settings.ACERAGE_CONVERT
    return area


class Farm(BaseModel):
    farm_name = models.CharField(max_length=250, unique=True, blank=True, null=True)
    farm_boundary = gis_models.PolygonField(null=False, srid=4326, blank=False)
    farm_area_acres = models.FloatField(
        default=0, validators=[MinValueValidator(0)], blank=True, null=True
    )
    crop_variety = models.ForeignKey(Crop_Variety, on_delete=models.SET_NULL, null=True)
    ward = models.ForeignKey(Ward, blank=False, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="farm_owner",
        null=True
    )
    slug = None

    def __str__(self):
        return f"{self.farm_area_acres}-{self.owner.full_name}"

    class Meta:
        verbose_name = "Farm"
        verbose_name_plural = "Farms"
        unique_together = ""
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def save(self, *args, **kwargs):
        self.farm_area_acres = get_sqm_by_wgs84_polygon(self.farm_boundary)
        super().save(*args, **kwargs)


class Pest_Control(BaseModel):
    pest_type = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=250)
    stage_pest = models.CharField(choices=PEST_STAGE.choices, max_length=50)
    action_threshold = models.CharField(max_length=50)
    action_threshold_risk = models.CharField(choices=PEST_STAGE.choices, max_length=50)
    stage_crop_growth = models.CharField(choices=GrowthStage.choices, max_length=50)
    cultural = models.CharField()
    cultural_description = models.TextField()
    biological = models.CharField()
    biological_description = models.TextField()
    slug = None

    def __str__(self):
        return f"{self.pest_type}"

    class Meta:
        verbose_name = "Pest Control Deprecated"
        verbose_name_plural = "Pest Controls Deprecated"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)


class Pest_Control_Modified(BaseModel):
    pest_type = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=250)
    stage_pest = models.CharField(choices=PEST_STAGE.choices, max_length=50)
    action_threshold = models.CharField(max_length=50)
    action_threshold_risk = models.CharField(choices=ACTION_THRESHOLD_RISK.choices, max_length=50)
    stage_crop_growth = models.CharField(choices=GrowthStage.choices, max_length=50)
    cultural = models.CharField()
    cultural_description = models.TextField()
    biological = models.CharField()
    biological_description = models.TextField()
    pest_presence_period = models.FloatField(blank=True, null=True, default=0, validators=[MinValueValidator(0)])
    no_of_plants_affected = models.FloatField(blank=True, null=True, default=0, validators=[MinValueValidator(0)])
    slug = None

    def __str__(self):
        return f"{self.pest_type}"

    class Meta:
        verbose_name = "Pest Control Modified"
        verbose_name_plural = "Pest Controls Modified"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)


class Planting_Information(BaseModel):
    farm = models.ForeignKey(Farm, on_delete=models.SET_NULL, related_name="planting_info_farm", null=True)
    crop_variety = models.ForeignKey(Crop_Variety, on_delete=models.SET_NULL, related_name="planting_info_crop_variety",
                                     null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transplanting_date = models.DateField()
    notification_end_date = models.DateField(blank=True)
    slug = None

    class Meta:
        unique_together = ("farm", "crop_variety", "transplanting_date")
        verbose_name = "Planting Information"
        verbose_name_plural = "Planting Information"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)

    def __str__(self):
        return self.farm.owner.first_name

    def clean(self):
        super().clean()
        # Validate that the transplanting_date is not greater than today
        if self.transplanting_date > datetime.date.today():
            raise ValidationError("Transplanting date cannot be greater than today.")

    def save(self, *args, **kwargs):
        self.clean()
        self.notification_end_date = self.transplanting_date + datetime.timedelta(
            days=self.crop_variety.max_maturity_in_days
        )
        super().save(*args, **kwargs)


class Any_Occurrence(BaseModel):
    yellow_buffer = gis_models.GeometryField(null=True, srid=4326, blank=True)
    red_buffer = gis_models.GeometryField(null=True, srid=4326, blank=True)
    green_buffer = gis_models.GeometryField(null=True, srid=4326, blank=True)
    slug = None

    class Meta:
        verbose_name = "Occurrence"
        verbose_name_plural = "Occurrences"
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
