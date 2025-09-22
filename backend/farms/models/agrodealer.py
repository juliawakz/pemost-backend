from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.choices import RoleChoices

User = get_user_model()


class AgroDealer(BaseModel):
    name = models.CharField(
        max_length=30,
        blank=False,
        null=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="agrodealers",
        null=True,
        blank=True
    )
    location = gis_models.PointField(
        geography=True,
        srid=4326
    )  # WGS84 lat/lon
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    email = models.EmailField(
        blank=True,
        null=True
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Agro Dealer")
        verbose_name_plural = _("Agro Dealers")
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

    def clean(self):
        if self.owner and self.owner.role != RoleChoices.AGRODEALER:
            raise ValidationError(_("Owner must have the role 'Agrodealer'."))

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation even outside forms/DRF
        super().save(*args, **kwargs)
