from django.contrib import admin
from farms.models import Plantation


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


admin.site.register(Plantation, PlantationAdmin)
