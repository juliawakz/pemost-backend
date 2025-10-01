from django.contrib import admin
from django.db import models
from django.contrib.gis.admin import OSMGeoAdmin
from django_json_widget.widgets import JSONEditorWidget
from farms.models import AgroDealer


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
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget}
    }
    save_on_top = True

    # map defaults (adjust center to your country/region)
    default_lon = 36_8219 * 100000  # Nairobi approx.
    default_lat = -1_2921 * 100000
    default_zoom = 10


admin.site.register(AgroDealer, AgroDealerAdmin)
