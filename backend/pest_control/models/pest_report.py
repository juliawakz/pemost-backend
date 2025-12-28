from app.models.farm import Farm
from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from pest_control.models.pest import Pest
from users.choices import RoleChoices

User = get_user_model()


class PestReport(BaseModel):
    """
    Model for reporting pest sightings by users.

    Users can report pests they encounter with location details,
    pest type, and quantity. All users except agrodealers can
    submit pest reports.
    """

    location = gis_models.PointField(
        srid=4326,
        help_text="Geographic location where the pest was observed"
    )

    farm = models.ForeignKey(
        Farm,
        on_delete=models.SET_NULL,
        related_name="pest_reports",
        null=True,
        blank=True,
        help_text="The farm where the pest was observed (optional)"
    )

    no_of_pests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of pests observed"
    )

    pest = models.ForeignKey(
        Pest,
        on_delete=models.CASCADE,
        related_name="pest_reports",
        help_text="The type of pest observed"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="submitted_pest_reports",
        null=True,
        blank=True,
        limit_choices_to=models.Q(
            role__in=[
                RoleChoices.SYSTEM_ADMIN,
                RoleChoices.SUPER_EXTENSION,
                RoleChoices.E_EXTENSION,
                RoleChoices.FARMER
            ]
        ),
        help_text="User who submitted the report (excluding agrodealers)"
    )

    slug = None

    class Meta:
        verbose_name = _("Pest Report")
        verbose_name_plural = _("Pest Reports")
        ordering = ("-created_at",)
        get_latest_by = ("-created_at",)
        unique_together = ("pest", "location")

    def __str__(self):
        farm_info = f" at {self.farm.name}" if self.farm else ""
        user_info = f" by {self.user.full_name}" if self.user else ""
        return (
            f"{self.no_of_pests} {self.pest.name}"
            f"{farm_info}{user_info}"
        )

    def clean(self):
        """Validate that the user is not an agrodealer."""
        if self.user and self.user.role == RoleChoices.AGRODEALER:
            raise ValidationError(
                _("Agrodealers are not allowed to submit pest reports.")
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
