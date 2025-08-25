from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from notifications.choices import MessageTypeChoices

User = get_user_model()


class Notification(BaseModel):
    slug = None
    channel = models.CharField(max_length=255, null=True, blank=True)
    message = models.JSONField(null=True, blank=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message_type = models.CharField(
        max_length=20,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.EMAIL,
    )
    is_read = models.BooleanField(default=False)
    message_to = models.ForeignKey(
        User,
        related_name="notification_user",
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ("-created_at",)
        get_latest_by = "-created_at"
