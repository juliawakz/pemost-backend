from base.models import BaseModel
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models.user import User


class Otp(BaseModel):
    token = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expiry_at = models.DateTimeField(
        default=timezone.make_aware(
            timezone.datetime.now() + timezone.timedelta(hours=1),
            timezone.get_default_timezone()
        )
    )

    slug = None
    metadata = None
    is_archived = None

    class Meta:
        verbose_name = _("Otp")
        verbose_name_plural = _("Otps")

    def __str__(self):
        return self.token
