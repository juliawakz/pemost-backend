from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

# Register your models here.
from crops.models import Crop, CropVariety, CropGrowthStage


class CropAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "updated_by",
        "created_at",
    ]
    list_filter = [
        "created_at",
        "updated_by"
    ]

    search_fields = [
        "name",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


class CropVarietyAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "crop",
        "climate",
        "min_maturity_days",
        "max_maturity_days",
        "min_yield",
        "max_yield",
        "created_at",
        "updated_by",
    ]
    list_filter = [
        "crop",
        "climate",
        "created_at",
        "updated_by",
    ]
    search_fields = [
        "name",
        "crop__name",
        "climate",
    ]
    list_per_page = 50
    save_on_top = True


class CropGrowthStageAdmin(admin.ModelAdmin):
    list_display = [
        "crop_variety",
        "growth_stage",
        "severity",
        "minimum_days",
        "maximum_days",
        "created_by",
        "updated_by",
        "created_at",
    ]
    list_filter = [
        "crop_variety"
    ]

    search_fields = [
        "name"
        ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


admin.site.register(Crop, CropAdmin)
admin.site.register(CropVariety, CropVarietyAdmin)
admin.site.register(CropGrowthStage, CropGrowthStageAdmin)
