from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel
from app.models.farm import Farm
from app.choices import AlertStatusChoices


class Alert(BaseModel):
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="alerts",
        help_text="The farm associated with this alert"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertStatusChoices.choices,
        default=AlertStatusChoices.NONE,
        help_text="The status/type of the alert (Yellow, Red, Green, None)"
    )
    read = models.BooleanField(
        default=False,
        help_text="Whether the alert has been read"
    )

    slug = None

    class Meta:
        verbose_name = _("Alert")
        verbose_name_plural = _("Alerts")
        ordering = ("-created_at",)

    def __str__(self):
        return f"Alert for {self.farm.name} - {self.alert_type}"
