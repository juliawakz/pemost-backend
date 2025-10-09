from django.db import models
from django.contrib.auth import get_user_model
from locations.models.ward import Ward
from users.choices import RoleChoices
from base.models import BaseModel
from users.models.super_extension import SuperExtensionOfficer

User = get_user_model()


class EExtensionOfficer(BaseModel):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='e_extension_profile'
    )
    wards = models.ManyToManyField(
        Ward,
        blank=False
    )
    super_extensions = models.ManyToManyField(
        SuperExtensionOfficer,
        related_name='managed_e_extensions',
        blank=True
    )
    is_managed = models.BooleanField(
        default=False
    )

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("E-Extension Officer")
        verbose_name_plural = _("E-Extension Officers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return f"{self.user.full_name}"

    def save(self, *args, **kwargs):
        self.user.role = RoleChoices.E_EXTENSION
        self.user.save()
        super().save(*args, **kwargs)
