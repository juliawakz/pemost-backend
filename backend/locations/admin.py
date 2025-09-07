from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

# Register your models here.
from locations.models import County, SubCounty, Ward


class CountyAdmin(admin.ModelAdmin):
    list_display = [
        "county_id",
        "name",
        "created_at",
    ]
    list_filter = [
        "created_at"
    ]

    search_fields = [
        "name",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


class SubCountyAdmin(admin.ModelAdmin):
    list_display = [
        "subcounty_id",
        "name",
        "county",
        "created_at",
    ]
    list_filter = [
        "created_at"
    ]

    search_fields = [
        "name",
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


class WardAdmin(admin.ModelAdmin):
    list_display = [
        "ward_id",
        "name",
        "subcounty",
        "created_at",
    ]
    list_filter = [
        "created_at"
    ]

    search_fields = [
        "name",
        "subcounty"
    ]
    list_per_page = 50
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    save_on_top = True


admin.site.register(County, CountyAdmin)
admin.site.register(SubCounty, SubCountyAdmin)
admin.site.register(Ward, WardAdmin)
