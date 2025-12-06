from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from locations.models.county import County
from users.choices import RoleChoices

User = get_user_model()


class SuperExtensionOfficer(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name='super_extension_users',
        limit_choices_to={'role': 'SUPER_EXTENSION'},
        unique=True,
        null=True,
        blank=True
    )
    counties = models.ManyToManyField(
        County,
        blank=False,
        related_name="super_extension_counties"
    )

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Super-Extension Officer")
        verbose_name_plural = _("Super-Extension Officers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        if self.user:
            return f"{self.user.full_name}"
        return f"Super-Extension Officer (Deleted User)"

    def save(self, *args, **kwargs):
        if self.user:
            self.user.role = RoleChoices.SUPER_EXTENSION
            self.user.save()
        super().save(*args, **kwargs)
