from django.db import models
from django.contrib.auth import get_user_model
from base.models import BaseModel
from locations.models.county import County
from users.choices import RoleChoices
from django.utils.translation import gettext as _

User = get_user_model()


class SuperExtensionOfficer(BaseModel):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='super_extension_profile'
    )
    counties = models.ManyToManyField(
        County,
        blank=True
    )

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Super Extension Officer")
        verbose_name_plural = _("Super Extension Officers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return f"{self.user.full_name}"

    def save(self, *args, **kwargs):
        self.user.role = RoleChoices.SUPER_EXTENSION
        self.user.save()
        super().save(*args, **kwargs)
