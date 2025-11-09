# serializers.py
from locations.models.ward import Ward
from locations.serializers.subcounty import MinimalSubCountySerializer
from rest_framework import serializers


class WardSerializer(serializers.ModelSerializer):
    subcounty = MinimalSubCountySerializer(read_only=True)

    class Meta:
        model = Ward
        fields = [
            "id",
            "ward_id",
            "subcounty",
            "name",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]


class MiniWardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = [
            "id",
            "ward_id",
            "name"
        ]
        read_only_fields = [
            "id"
        ]
