from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from farms.utils.farm import FarmUtils
from locations.models import Ward

User = get_user_model()
farm_util = FarmUtils()


class Farm(BaseModel):
    name = models.CharField(
        max_length=250,
        unique=True,
        blank=True,
        null=True
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        null=False,
        blank=False
    )
    size = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.SET_NULL,
        null=True,
        blank=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="farms",
        null=True
    )

    slug = None

    def clean(self):
        if self.owner and self.ward and self.ward not\
                in self.owner.wards.all():
            raise ValidationError(
                "Farm ward must be one of the wards\
                    where the owner is registered."
            )

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation on save
        self.size = farm_util.get_sqm_by_wgs84_polygon(self.boundary)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or 'Unnamed'} - {self.owner.first_name} {self.owner.last_name}"
