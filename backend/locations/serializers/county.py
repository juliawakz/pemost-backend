# serializers.py
from locations.models.county import County
from rest_framework import serializers


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = [
            "id",
            "county_id",
            "name",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]


class MinimalCountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = [
            "id",
            "county_id",
            "name"
        ]
        read_only_fields = [
            "id"
        ]
