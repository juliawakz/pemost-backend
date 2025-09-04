from base.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.choices import RoleChoices
from django.contrib.auth import get_user_model

User = get_user_model()


class Role(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_role'
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.FARMER
    )

    slug = None
    metadata = None
    is_archived = None

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return f"{self.user.full_name} - {self.get_role_display()}"
