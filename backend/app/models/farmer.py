from django.db import models
from django.contrib.auth import get_user_model
from users.choices import RoleChoices
from base.models import BaseModel
from users.models.e_extension import EExtensionOfficer
from django.utils.translation import gettext as _

User = get_user_model()


class Farmer(BaseModel):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='farmer_profile'
    )
    e_extensions = models.ManyToManyField(
        EExtensionOfficer,
        related_name='managed_farmers',
        blank=True
    )
    is_managed = models.BooleanField(
        default=False
    )

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Farmer")
        verbose_name_plural = _("Farmers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return f"{self.user.full_name}"

    def save(self, *args, **kwargs):
        self.user.role = RoleChoices.FARMER
        self.user.save()
        super().save(*args, **kwargs)
