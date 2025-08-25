import csv
from datetime import datetime

from app.models import (
    Any_Occurrence,
    County,
    Crop_Type,
    Crop_Variety,
    Farm,
    Growth_Stage,
    Pest_Control,
    Pest_Control_Modified,
    Planting_Information,
    SubCounty,
    Ward,
)
from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from django.http import HttpResponse


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment;" "filename{}.csv".format(
        opts.verbose_name
    )
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many and not field.one_to_one
    ]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)

    return response


export_to_csv.short_description = "Export to CSV"  # short description


@admin.register(Crop_Variety)
class CropVarietyAdmin(admin.ModelAdmin):
    list_display = [
        "crop_type",
        "crop_variety",
        "min_maturity_in_days",
        "max_maturity_in_days",
        "min_annual_rainfall_mm",
        "created_at"
    ]
    search_fields = ("crop_type", "crop_variety")


@admin.register(Any_Occurrence)
class OccurrenceAdmin(GeoModelAdmin):
    list_display = ["id", "created_at"]


@admin.register(Growth_Stage)
class GrowthStageAdmin(admin.ModelAdmin):
    list_display = ["crop_variety", "growth_stage", "severity", "created_at"]


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "county_num", "created_at"]
    search_fields = ("name", "county_num")


@admin.register(SubCounty)
class SubCountyAdmin(GeoModelAdmin):
    list_display = ["id", "name", "county", "created_at"]
    search_fields = ("name", "county")


@admin.register(Ward)
class WardAdmin(GeoModelAdmin):
    list_display = ["id", "name", "subcounty", "created_at"]
    search_fields = ("name", "subcounty")


@admin.register(Farm)
class FarmAdmin(GeoModelAdmin):
    list_display = ["farm_area_acres", "owner", "created_at", "updated_at"]
    actions = [export_to_csv]


@admin.register(Crop_Type)
class CropTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    actions = [export_to_csv]


@admin.register(Pest_Control)
class PestControlAdmin(admin.ModelAdmin):
    list_display = ["id", "pest_type", "stage_pest", "created_at"]
    actions = [export_to_csv]


@admin.register(Pest_Control_Modified)
class PestControlModifiedAdmin(admin.ModelAdmin):
    list_display = ["id", "pest_type", "stage_pest", "stage_crop_growth", "created_at"]
    actions = [export_to_csv]


@admin.register(Planting_Information)
class PlantingInformationAdmin(admin.ModelAdmin):
    list_display = ["id", "farm", "crop_variety", "transplanting_date", "notification_end_date", "created_at"]
    actions = [export_to_csv]
