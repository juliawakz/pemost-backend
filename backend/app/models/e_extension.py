from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from locations.models.ward import Ward
from users.choices import RoleChoices
from base.models import BaseModel
from app.models.super_extension import SuperExtensionOfficer

User = get_user_model()


class EExtensionOfficer(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='e_extension_users',
        limit_choices_to={'role': 'E_EXTENSION'}
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
    is_visible = models.BooleanField(
        default=False,
        help_text="If True, e-extension is visible to super extension"
        "officers allowed in their county"
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
