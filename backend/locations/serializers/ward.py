# serializers.py
from locations.models.ward import Ward
from locations.serializers.county import MinimalCountySerializer
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field


class WardSerializer(serializers.ModelSerializer):
    county = serializers.SerializerMethodField()

    class Meta:
        model = Ward
        fields = [
            "id",
            "ward_id",
            "county",
            "name",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]

    @extend_schema_field(MinimalCountySerializer(allow_null=True))
    def get_county(self, obj):
        """Get county data from ward's subcounty"""
        if obj.subcounty and obj.subcounty.county:
            return MinimalCountySerializer(obj.subcounty.county).data
        return None


class MiniWardSerializer(serializers.ModelSerializer):
    county = serializers.SerializerMethodField()

    class Meta:
        model = Ward
        fields = [
            "id",
            "ward_id",
            "name",
            "county"
        ]
        read_only_fields = [
            "id"
        ]

    @extend_schema_field(MinimalCountySerializer(allow_null=True))
    def get_county(self, obj):
        """Get county data from ward's subcounty"""
        if obj.subcounty and obj.subcounty.county:
            return MinimalCountySerializer(obj.subcounty.county).data
        return None
