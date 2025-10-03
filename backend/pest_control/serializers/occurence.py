from rest_framework import serializers
from pest_control.models.occurence import Occurrence


class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occurrence
        fields = [
            "id",
            "yellow_buffer",
            "red_buffer",
            "green_buffer",
            "created_at",
            "updated_at"
        ]
        read_only = [
            "id",
            "created_at",
            "updated_at"
        ]
