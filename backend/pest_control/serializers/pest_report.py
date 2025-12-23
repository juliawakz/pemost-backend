from pest_control.models.pest_report import PestReport
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from users.serializers.user import MiniUserReadSerializer


class PestReportWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating pest reports.
    """
    class Meta:
        model = PestReport
        fields = [
            "id",
            "location",
            "farm",
            "no_of_pests",
            "pest",
            "user",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class PestReportReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading pest report details.
    """
    user = MiniUserReadSerializer(read_only=True)
    pest_name = serializers.CharField(
        source='pest.name',
        read_only=True
    )
    pest_scientific_name = serializers.CharField(
        source='pest.scientific_name',
        read_only=True
    )
    farm_name = serializers.CharField(
        source='farm.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = PestReport
        fields = [
            "id",
            "location",
            "farm",
            "farm_name",
            "no_of_pests",
            "pest",
            "pest_name",
            "pest_scientific_name",
            "user",
            "created_at",
            "updated_at"
        ]


class MiniPestReportSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing pest reports.
    """
    pest_name = serializers.CharField(
        source='pest.name',
        read_only=True
    )
    farm_name = serializers.CharField(
        source='farm.name',
        read_only=True,
        allow_null=True
    )
    user_name = serializers.CharField(
        source='user.full_name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = PestReport
        fields = [
            "id",
            "pest_name",
            "farm_name",
            "no_of_pests",
            "user_name",
            "created_at"
        ]


class PestReportGeoSerializer(GeoFeatureModelSerializer):
    """
    GeoJSON serializer for pest reports with location data.
    """
    pest_name = serializers.CharField(
        source='pest.name',
        read_only=True
    )
    farm_name = serializers.CharField(
        source='farm.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = PestReport
        geo_field = "location"
        fields = [
            "id",
            "pest_name",
            "farm_name",
            "no_of_pests",
            "created_at"
        ]
