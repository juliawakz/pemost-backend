# serializers.py
from rest_framework import serializers
from locations.models.subcounty import SubCounty


class SubCountySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCounty
        fields = [
            "id",
            "subcounty_id",
            "name",
            "county",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]
