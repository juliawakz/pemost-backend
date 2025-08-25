from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from users.models import Otp, User


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "type",
        "is_verified",
        "is_archived",
        "created_at",
    ]
    list_filter = ["created_at", "updated_at", "type"]
    search_fields = [
        "email",
        "id",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


class OtpAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "token",
        "expiry_at",
        "created_at",
    ]
    list_filter = [
        "created_at",
    ]

    search_fields = [
        "user__email",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


admin.site.register(User, UserAdmin)
admin.site.register(Otp, OtpAdmin)
