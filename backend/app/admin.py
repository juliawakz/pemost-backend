from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from users.models import (
    EExtensionWorkRequest,
    FarmerWorkRequest,
    Otp,
    User,
    EExtensionOfficer,
    SuperExtensionOfficer,
    Agrodealer
)


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "role",
        "is_verified",
        "is_archived",
        "created_at",
    ]
    list_filter = ["created_at", "updated_at", "role", "is_verified"]
    search_fields = [
        "email",
        "id",
        "first_name",
        "last_name",
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


class EExtensionWorkRequestAdmin(admin.ModelAdmin):
    list_display = [
        "e_extension",
        "super_extension",
        "status",
        "notification_sent",
        "created_at",
        "responded_at",
    ]
    list_filter = ["status", "notification_sent", "created_at"]
    search_fields = ["e_extension__email", "super_extension__email"]
    list_per_page = 50
    save_on_top = True


class FarmerWorkRequestAdmin(admin.ModelAdmin):
    list_display = [
        "farmer",
        "e_extension",
        "status",
        "notification_sent",
        "created_at",
        "responded_at",
    ]
    list_filter = ["status", "notification_sent", "created_at"]
    search_fields = ["farmer__email", "e_extension__email"]
    list_per_page = 50
    save_on_top = True


class EExtensionOfficerAdmin(admin.ModelAdmin):
    list_display = ["user", "is_visible", "created_at"]
    list_filter = ["is_visible", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


class SuperExtensionOfficerAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


class AgrodealerAdmin(admin.ModelAdmin):
    list_display = ["user", "is_visible", "created_at"]
    list_filter = ["is_visible", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


admin.site.register(User, UserAdmin)
admin.site.register(Otp, OtpAdmin)
admin.site.register(EExtensionWorkRequest, EExtensionWorkRequestAdmin)
admin.site.register(FarmerWorkRequest, FarmerWorkRequestAdmin)
admin.site.register(EExtensionOfficer, EExtensionOfficerAdmin)
admin.site.register(SuperExtensionOfficer, SuperExtensionOfficerAdmin)
admin.site.register(Agrodealer, AgrodealerAdmin)
