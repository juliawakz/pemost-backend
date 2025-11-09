from app.models import (
    Agrodealer,
    EExtensionOfficer,
    EExtensionWorkRequest,
    Farm,
    FarmerWorkRequest,
    SuperExtensionOfficer,
)
from app.models.plantation import Plantation
from base.utils import ExportActionsMixin
from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


class FarmAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = [
        "name",
        "calc_size",
        "user_size",
        "ward",
        "alert_status",
        "farmer",
        "is_visible",
        "is_archived",
        "created_at",
    ]
    list_filter = ["created_at", "updated_at", "is_visible", "ward"]
    search_fields = [
        "ward",
        "id",
        "name",
        "farmer"
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


class EExtensionWorkRequestAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
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


class FarmerWorkRequestAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = [
        "e_extension",
        "status",
        "notification_sent",
        "created_at",
        "responded_at",
    ]
    list_filter = ["status", "notification_sent", "created_at"]
    search_fields = ["e_extension__email"]
    list_per_page = 50
    save_on_top = True


class EExtensionOfficerAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = ["user", "is_visible", "created_at"]
    list_filter = ["is_visible", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


class SuperExtensionOfficerAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = ["user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


class AgrodealerAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = ["user", "name", "ward", "is_visible", "created_at"]
    list_filter = ["is_visible", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_per_page = 50
    save_on_top = True


class PlantationAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = [
        "id",
        "farm",
        "crop_variety",
        "transplanting_date",
        "notification_end_date",
        "is_matured",
        "is_archived",
        "created_at",
    ]
    list_filter = [
        "is_matured",
        "is_archived",
        "crop_variety",
        "transplanting_date",
        "created_at",
    ]
    search_fields = [
        "farm__name",
        "farm__farmer__first_name",
        "farm__farmer__last_name",
        "crop_variety__name",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True
    readonly_fields = [
        "notification_end_date",
        "created_at",
        "updated_at"
    ]

    fieldsets = (
        ("Plantation Information", {
            "fields": (
                "farm",
                "crop_variety",
                "transplanting_date",
            )
        }),
        ("Maturity Status", {
            "fields": (
                "notification_end_date",
                "is_matured",
            )
        }),
        ("Metadata", {
            "fields": (
                "is_archived",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )

    def process_csv_row(self, row):
        """
        Custom CSV row processing for Plantation model.
        """
        from crops.models.crop_variety import CropVariety
        from datetime import datetime

        # Get required foreign keys
        farm_id = row.get('farm', '').strip()
        crop_variety_id = row.get('crop variety', '').strip()

        if not farm_id or not crop_variety_id:
            raise ValueError("Both farm and crop variety are required")

        try:
            farm = Farm.objects.get(id=farm_id)
        except Farm.DoesNotExist:
            raise ValueError(f"Farm with ID {farm_id} not found")

        try:
            crop_variety = CropVariety.objects.get(id=crop_variety_id)
        except CropVariety.DoesNotExist:
            raise ValueError(f"CropVariety with ID {crop_variety_id} not found")

        # Parse date
        transplanting_date_str = row.get('transplanting date', '').strip()
        if not transplanting_date_str:
            raise ValueError("transplanting date is required")

        try:
            transplanting_date = datetime.strptime(
                transplanting_date_str, "%d/%m/%Y"
            ).date()
        except ValueError:
            raise ValueError(
                f"Invalid date format: {transplanting_date_str}. "
                f"Use DD/MM/YYYY"
            )

        # Create or update plantation
        plantation, created = Plantation.objects.update_or_create(
            farm=farm,
            crop_variety=crop_variety,
            transplanting_date=transplanting_date,
            defaults={
                'is_matured': row.get('is matured', 'False').strip().lower()
                in ['true', '1', 'yes']
            }
        )

        return 'created' if created else 'updated'


admin.site.register(EExtensionWorkRequest, EExtensionWorkRequestAdmin)
admin.site.register(FarmerWorkRequest, FarmerWorkRequestAdmin)
admin.site.register(EExtensionOfficer, EExtensionOfficerAdmin)
admin.site.register(SuperExtensionOfficer, SuperExtensionOfficerAdmin)
admin.site.register(Agrodealer, AgrodealerAdmin)
admin.site.register(Farm, FarmAdmin)
admin.site.register(Plantation, PlantationAdmin)
