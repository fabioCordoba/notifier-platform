from rest_framework import serializers


class ApiKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class ApiKeyRevokeSerializer(serializers.Serializer):
    pass
