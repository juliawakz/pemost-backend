from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from alerts.models import Alert
from app.serializers.farm import MiniFarmReadSerializer
from app.models.plantation import Plantation


class MiniAlertSerializer(serializers.ModelSerializer):
    """Minimal representation of an Alert."""
    farm = MiniFarmReadSerializer(read_only=True)
    status = serializers.CharField(source='alert_type', read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id",
            "farm",
            "status",
            "read",
            "created_at",
        ]


class AlertReadSerializer(serializers.ModelSerializer):
    """
    Full representation of an Alert including plantation information.
    """
    farm = MiniFarmReadSerializer(read_only=True)
    type = serializers.CharField(source='alert_type', read_only=True)
    plantation_info = serializers.SerializerMethodField()
    pest_and_interventions = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = [
            "id",
            "type",
            "farm",
            "plantation_info",
            "pest_and_interventions",
            "read",
            "created_at",
        ]

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'transplanting_date': {'type': 'string', 'format': 'date'},
            'crop_variety': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'name': {'type': 'string'},
                }
            }
        },
        'nullable': True
    })
    def get_plantation_info(self, obj):
        """
        Get the active plantation information for the farm.
        Returns the most recent active (non-matured) plantation,
        or the most recent plantation if no active one exists.
        """
        if not obj.farm:
            return None

        # Try to get the most recent active plantation
        plantation = Plantation.objects.filter(
            farm=obj.farm,
            is_matured=False,
            is_archived=False
        ).order_by('-created_at').first()

        # If no active plantation, get the most recent one
        if not plantation:
            plantation = Plantation.objects.filter(
                farm=obj.farm,
                is_archived=False
            ).order_by('-created_at').first()

        if not plantation:
            return None

        crop_id = (
            str(plantation.crop_variety.id)
            if plantation.crop_variety else None
        )
        crop_name = (
            plantation.crop_variety.name
            if plantation.crop_variety else None
        )

        return {
            'transplanting_date': plantation.transplanting_date,
            'crop_variety': {
                'id': crop_id,
                'name': crop_name,
            } if plantation.crop_variety else None
        }

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'interventions': {
                'type': 'array',
                'items': {
                    'oneOf': [
                        {'type': 'string'},
                        {
                            'type': 'object',
                            'properties': {
                                'stage': {'type': 'string'},
                                'name': {'type': 'string'},
                                'scientific_name': {'type': 'string'},
                                'presence_period': {'type': 'string'},
                                'no_of_plants_affected': {'type': 'string'},
                                'action_threshold': {'type': 'string'},
                                'action_threshold_risk': {'type': 'string'},
                                'crop_growth_stage': {'type': 'string'},
                                'cultural': {'type': 'string'},
                                'cultural_description': {'type': 'string'},
                                'biological': {'type': 'string'},
                                'biological_description': {'type': 'string'}
                            }
                        }
                    ]
                }
            }
        },
        'nullable': True
    })
    def get_pest_and_interventions(self, obj):
        """
        Get pest and intervention information from farm metadata.
        Returns the pest_and_interventions data stored in the farm's
        metadata field.
        """
        if not obj.farm or not obj.farm.metadata:
            return None

        return obj.farm.metadata.get('pest_and_interventions', None)
