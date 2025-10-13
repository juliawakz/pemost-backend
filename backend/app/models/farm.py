import math

from app.models.e_extension import EExtensionOfficer
from base.models import BaseModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from locations.models import Ward

User = get_user_model()


class Farm(BaseModel):
    name = models.CharField(
        max_length=250,
        unique=True
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        null=False,
        blank=False
    )
    user_size = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    calc_size = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        blank=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="farm_users",
        limit_choices_to={'role': 'FARMER'}
    )
    e_extensions = models.ManyToManyField(
        EExtensionOfficer,
        related_name='managed_farms',
        blank=True
    )
    is_visible = models.BooleanField(
        default=False,
        help_text="If True, farmer is visible to allowed " \
        "e-extension officers in their ward"
    )

    slug = None
    metadata = None

    def clean(self):
        """Validate farm data"""
        if self.user and not self.user.is_farmer():
            raise ValidationError(
                "Farm user must have the role 'FARMER'."
            )

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation on save
        self.calc_size = self.get_sqm_by_wgs84_polygon(self.boundary)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or 'Unnamed'} - {self.user.first_name}\
            {self.user.last_name}"

    def get_sqm_by_wgs84_polygon(self, geom):
        """
        Converts wgs 84 coordinates(lat/lon) to projected coordinates(meters)
        and get the acreage of a farm
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
