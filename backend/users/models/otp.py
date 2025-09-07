from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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

    @property
    def is_valid(self) -> bool:
        """Check if OTP has not expired."""
        return self.expiry_at >= timezone.now()
