from django.contrib.gis.geos import Point
from pest_control.models.pest_report import PestReport
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from users.serializers.user import MiniUserReadSerializer


class PestReportWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating pest reports.
    """
    longitude = serializers.FloatField(
        write_only=True,
        help_text="Longitude of the pest location"
    )
    latitude = serializers.FloatField(
        write_only=True,
        help_text="Latitude of the pest location"
    )

    class Meta:
        model = PestReport
        fields = [
            "id",
            "longitude",
            "latitude",
            "farm",
            "no_of_pests",
            "pest",
            "user",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        longitude = validated_data.pop('longitude')
        latitude = validated_data.pop('latitude')

        # Create Point from longitude and latitude
        location = Point(longitude, latitude, srid=4326)
        validated_data['location'] = location

        return super().create(validated_data)

    def update(self, instance, validated_data):
        longitude = validated_data.pop('longitude', None)
        latitude = validated_data.pop('latitude', None)

        if longitude is not None and latitude is not None:
            instance.location = Point(longitude, latitude, srid=4326)

        return super().update(instance, validated_data)


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
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = PestReport
        fields = [
            "id",
            "longitude",
            "latitude",
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

    def get_longitude(self, obj):
        """Extract longitude from location Point."""
        return obj.location.x if obj.location else None

    def get_latitude(self, obj):
        """Extract latitude from location Point."""
        return obj.location.y if obj.location else None


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
