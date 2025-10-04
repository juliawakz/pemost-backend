from pest_control.models.pest_occurence import PestOccurrence
from pest_control.utils.pest_occurence import PestOccurenceUtils
from rest_framework import serializers

pest_occurrence_utils = PestOccurenceUtils()


class PestOccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestOccurrence
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


class ProcessOccurrenceSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.DictField())

    def validate(self, attrs):

        pest_occurrence_utils.get_occurence_and_classification(
            data=attrs.get("data")
        )

        return attrs
