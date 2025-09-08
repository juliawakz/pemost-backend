from rest_framework import serializers


class RoleChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
