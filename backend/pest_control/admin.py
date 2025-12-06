from base.utils import ExportActionsMixin
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from pest_control.models import Pest, PestOccurrence, PestReport


class PestAdmin(ExportActionsMixin, admin.ModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = [
        "name",
        "scientific_name",
        "stage",
        "crop_growth_stage",
        "action_threshold",
        "action_threshold_risk",
        "presence_period",
        "no_of_plants_affected",
        "created_at",
    ]
    list_filter = [
        "stage",
        "action_threshold_risk",
        "crop_growth_stage",
        "created_at",
    ]
    search_fields = [
        "name",
        "scientific_name",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "name",
                "scientific_name",
                "stage",
            )
        }),
        ("Threshold & Risk", {
            "fields": (
                "action_threshold",
                "action_threshold_risk",
                "crop_growth_stage",
            )
        }),
        ("Control Methods", {
            "fields": (
                "cultural",
                "cultural_description",
                "biological",
                "biological_description",
            )
        }),
        ("Impact Metrics", {
            "fields": (
                "presence_period",
                "no_of_plants_affected",
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
        Custom CSV row processing for Pest model.
        """
        # Create or update pest
        pest, created = Pest.objects.update_or_create(
            name=row.get('name', '').strip(),
            scientific_name=row.get('scientific name', '').strip(),
            stage=row.get('stage', '').strip().lower(),
            action_threshold=row.get('action threshold', '').strip(),
            action_threshold_risk=row.get(
                'action threshold risk', ''
            ).strip().lower(),
            crop_growth_stage=row.get('growth stage', '').strip().lower(),
            cultural=row.get('cultural', '').strip(),
            biological=row.get('biological', '').strip(),
            defaults={
                'cultural_description': row.get(
                    'cultural description', ''
                ).strip(),
                'biological_description': row.get(
                    'biological description', ''
                ).strip(),
                'presence_period': float(
                    row.get('presence period', 0) or 0
                ),
                'no_of_plants_affected': float(
                    row.get('no of plants affected', 0) or 0
                ),
            }
        )

        return 'created' if created else 'updated'


class PestOccurrenceAdmin(ExportActionsMixin, GISModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = [
        "id",
        "created_at",
        "is_archived",
    ]
    list_filter = [
        "created_at",
        "is_archived",
    ]
    search_fields = ["id"]
    list_per_page = 50
    save_on_top = True
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Geographic Buffers", {
            "fields": (
                "yellow_buffer",
                "red_buffer",
                "green_buffer",
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


class PestReportAdmin(ExportActionsMixin, GISModelAdmin):
    actions = ['export_to_csv', 'download_sample_csv']
    list_display = [
        "id",
        "pest",
        "farm",
        "no_of_pests",
        "user",
        "created_at",
    ]
    list_filter = [
        "pest",
        "farm",
        "created_at",
        "is_archived",
    ]
    search_fields = [
        "pest__name",
        "pest__scientific_name",
        "farm__name",
        "user__email",
        "user__first_name",
        "user__last_name"
    ]
    list_per_page = 50
    save_on_top = True
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["pest", "farm", "user"]

    fieldsets = (
        ("Report Details", {
            "fields": (
                "pest",
                "farm",
                "no_of_pests",
                "user",
            )
        }),
        ("Location", {
            "fields": (
                "location",
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


admin.site.register(Pest, PestAdmin)
admin.site.register(PestOccurrence, PestOccurrenceAdmin)
admin.site.register(PestReport, PestReportAdmin)
