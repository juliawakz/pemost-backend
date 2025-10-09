from django.db import models
from django.contrib.auth import get_user_model
from users.choices import RoleChoices
from base.models import BaseModel
from django.utils.translation import gettext as _

User = get_user_model()


class Agrodealer(BaseModel):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='agrodealer_profile'
    )
    is_visible = models.BooleanField(
        default=True
    )

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Agrodealr")
        verbose_name_plural = _("Agrodealers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return f"{self.user.full_name}"

    def save(self, *args, **kwargs):
        self.user.role = RoleChoices.AGRODEALER
        self.user.save()
        super().save(*args, **kwargs)
