from django.contrib import admin
from alerts.models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'farm',
        'alert_type',
        'read',
        'created_at'
    )
    list_filter = ('alert_type', 'read', 'created_at')
    search_fields = ('farm__name', 'farm__farmer__first_name',
                     'farm__farmer__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
