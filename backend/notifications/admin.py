from django.contrib import admin
from notifications.models import Notification


@admin.register(Notification)
class MessageTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "subject",
        "is_read"
    )
