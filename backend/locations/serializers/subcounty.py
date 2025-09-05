# serializers.py
from rest_framework import serializers
from locations.models.subcounty import SubCounty
from locations.serializers.county import MinimalCountySerializer


class SubCountySerializer(serializers.ModelSerializer):
    county = MinimalCountySerializer(read_only=True)

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


class MinimalSubCountySerializer(serializers.ModelSerializer):
    county = MinimalCountySerializer(read_only=True)

    class Meta:
        model = SubCounty
        fields = [
            "id",
            "subcounty_id",
            "name",
            "county"
        ]
        read_only_fields = [
            "id"
        ]
