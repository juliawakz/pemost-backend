from base.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from locations.models.subcounty import SubCounty


class Ward(BaseModel):
    ward_id = models.PositiveIntegerField(
        unique=True,
        help_text=_("The unique id assigned to the ward.")
    )
    name = models.CharField(
        max_length=100,
        help_text=_("The unique name assigned to the ward.")
    )
    subcounty = models.ForeignKey(
        SubCounty,
        on_delete=models.CASCADE,
        related_name="wards"
    )

    slug = None
    metadata = None
    is_archived = None

    class Meta:
        verbose_name = _("Ward")
        verbose_name_plural = _("Wards")
        unique_together = ("name", "subcounty")

    def __str__(self):
        return f"{self.name} ({self.subcounty.name})({self.subcounty.county.name})"
