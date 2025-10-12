import logging

from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from geopy.geocoders import Nominatim
from locations.models.ward import Ward
from phonenumber_field.modelfields import PhoneNumberField
from users.choices import RoleChoices

logger = logging.getLogger(__name__)
User = get_user_model()


class Agrodealer(BaseModel):
    name = models.CharField(
        max_length=30,
        blank=False,
        null=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="agrodealers",
        limit_choices_to={'role': 'AGRODEALER'}
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE
    )
    location = gis_models.PointField(
        geography=True,
        srid=4326
    )  # WGS84 lat/lon
    address = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    is_visible = models.BooleanField(
        default=True
    )

    slug = None
    metadata = None

    class Meta:
        verbose_name = _("Agro Dealer")
        verbose_name_plural = _("Agro Dealers")
        ordering = ("name",)
        unique_together = ("location", "name", "user")

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

    def clean(self):
        if self.user and self.user.role != RoleChoices.AGRODEALER:
            raise ValidationError(
                _("User must have the role 'Agrodealer'.")
            )

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation even outside forms/DRF

        # Always overwrite address with reverse geocode result
        if self.location:
            try:
                geolocator = Nominatim(user_agent="agrodealer_app")
                location = geolocator.reverse(
                    (self.latitude, self.longitude),
                    language="en"
                )
                if location and location.address:
                    self.address = location.address
                else:
                    self.address = None
            except Exception as e:
                logger.warning(
                    f"Nominatim reverse geocoding failed: {e}"
                )
                self.address = None  # fallback to null if lookup fails

        super().save(*args, **kwargs)
