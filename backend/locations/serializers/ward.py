# serializers.py
from locations.models.ward import Ward
from locations.serializers.county import MinimalCountySerializer
from rest_framework import serializers


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

    def get_county(self, obj):
        """Get county data from ward's subcounty"""
        if obj.subcounty and obj.subcounty.county:
            return MinimalCountySerializer(obj.subcounty.county).data
        return None
