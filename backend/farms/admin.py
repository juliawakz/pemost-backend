from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from farms.models import AgroDealer, Farm, Plantation


class FarmAdmin(OSMGeoAdmin):
    list_display = [
        "id",
        "name",
        "owner",
        "ward",
        "size",
        "created_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
        "ward",
    ]
    search_fields = [
        "name",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
    ]
    list_per_page = 50
    save_on_top = True
    default_lon = 36_8219 * 100000  # adjust to your region (Nairobi approx.)
    default_lat = -1_2921 * 100000
    default_zoom = 12


class AgroDealerAdmin(OSMGeoAdmin):
    list_display = [
        "id",
        "name",
        "owner",
        "ward",
        "phone_number",
        "email",
        "address",
        "created_at",
    ]
    list_filter = [
        "ward",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "phone_number",
        "email",
        "address",
    ]
    list_per_page = 50
    save_on_top = True

    # map defaults (adjust center to your country/region)
    default_lon = 36_8219 * 100000  # Nairobi approx.
    default_lat = -1_2921 * 100000
    default_zoom = 10


class PlantationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "farm",
        "get_owner",
        "crop_variety",
        "transplanting_date",
        "notification_end_date",
        "created_at",
    ]
    list_filter = [
        "transplanting_date",
        "notification_end_date",
        "created_at",
    ]
    search_fields = [
        "farm__name",
        "farm__owner__first_name",
        "farm__owner__last_name",
        "crop_variety__name",
    ]
    date_hierarchy = "transplanting_date"
    list_per_page = 50
    save_on_top = True

    def get_owner(self, obj):
        return f"{obj.farm.owner.first_name} {obj.farm.owner.last_name}" if obj.farm and obj.farm.owner else "-"
    get_owner.short_description = "Owner"


admin.site.register(Farm, FarmAdmin)
admin.site.register(AgroDealer, AgroDealerAdmin)
admin.site.register(Plantation, PlantationAdmin)
