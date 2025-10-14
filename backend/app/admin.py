from app.models import (
    Agrodealer,
    EExtensionOfficer,
    EExtensionWorkRequest,
    Farm,
    FarmerWorkRequest,
    SuperExtensionOfficer,
)
from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


class FarmAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "calc_size",
        "user_size",
        "ward",
        "user",
        "is_visible",
        "is_archived",
        "created_at",
    ]
    list_filter = ["created_at", "updated_at", "is_visible", "ward"]
    search_fields = [
        "ward",
        "id",
        "name"
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
    list_display = ["user", "name", "ward", "is_visible", "created_at"]
    list_filter = ["is_visible", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


admin.site.register(EExtensionWorkRequest, EExtensionWorkRequestAdmin)
admin.site.register(FarmerWorkRequest, FarmerWorkRequestAdmin)
admin.site.register(EExtensionOfficer, EExtensionOfficerAdmin)
admin.site.register(SuperExtensionOfficer, SuperExtensionOfficerAdmin)
admin.site.register(Agrodealer, AgrodealerAdmin)
admin.site.register(Farm, FarmAdmin)
