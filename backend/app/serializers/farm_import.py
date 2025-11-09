from rest_framework import serializers
from app.utils.farm_import import FarmImportUtil

farm_import = FarmImportUtil()


class FarmsImportSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        shapefile = validated_data.pop("file", None)
        info = farm_import.import_farms(shapefile)
        return info
