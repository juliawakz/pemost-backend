from django.contrib import admin
from django.db import models
from django.contrib.gis.admin import OSMGeoAdmin
from django_json_widget.widgets import JSONEditorWidget
from farms.models import Farm, AgroDealer, Plantation


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
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget}
    }
    save_on_top = True
    default_lon = 36_8219 * 100000  # adjust to your region (Nairobi approx.)
    default_lat = -1_2921 * 100000
    default_zoom = 12


admin.site.register(Farm, FarmAdmin)
