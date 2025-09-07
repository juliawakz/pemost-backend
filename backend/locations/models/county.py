from base.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class County(BaseModel):
    county_id = models.PositiveIntegerField(
        unique=True,
        help_text=_("The unique number assigned to the county.")
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("The unique name assigned to the county.")
    )

    slug = None
    metadata = None
    is_archived = None

    class Meta:
        verbose_name = _("County")
        verbose_name_plural = _("Counties")

    def __str__(self):
        return self.name
