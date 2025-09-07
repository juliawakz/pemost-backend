from base.models import BaseModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Otp(BaseModel):
    token = models.CharField(
        max_length=6
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    expiry_at = models.DateTimeField()

    slug = None
    metadata = None
    is_archived = None

    class Meta:
        verbose_name = _("Otp")
        verbose_name_plural = _("Otps")

    def __str__(self):
        return f"{self.user.full_name} - {self.token}"
