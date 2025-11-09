from base.utils import ExportActionsMixin
from django.contrib import admin
from notifications.models import Notification


@admin.register(Notification)
class MessageTypeAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = (
        "id",
        "message",
        "subject",
        "is_read"
    )
