from base.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from locations.models.county import County


class SubCounty(BaseModel):
    subcounty_id = models.PositiveIntegerField(
        unique=True,
        help_text=_("The unique id assigned to the subcounty.")
    )
    name = models.CharField(
        max_length=100,
        help_text=_("The unique name assigned to the subcounty.")
    )
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE,
        related_name="subcounties"
    )

    slug = None
    metadata = None
    is_archived = None

    class Meta:
        verbose_name = _("SubCounty")
        verbose_name_plural = _("SubCounties")
        unique_together = ("name", "county")
        ordering = ("subcounty_id",)

    def __str__(self):
        return f"{self.name} ({self.county.name})"
