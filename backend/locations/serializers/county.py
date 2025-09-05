# serializers.py
from rest_framework import serializers
from locations.models.county import County


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
