from django.db import models
from django.utils.translation import gettext_lazy as _


class PEST_STAGE(models.TextChoices):
    """
    Pest Stage
    """

    LARVAE = "larvae", _("Larvae")
    EGGS = "eggs", _("Eggs")
    NYMPH = "nymph", _("Nymph")
    PUPAE = "pupae", _("Pupae")
    ADULT = "adult", _("Adult")


class ACTION_THRESHOLD_RISK(models.TextChoices):
    """
    Risk Levels
    """
    HIGH = "high", _("High")
    LOW = "low", _("Low")
    MODERATE = "moderate", _("Moderate")
    NONE = "none", _("None")
