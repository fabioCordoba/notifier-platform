from rest_framework import serializers
from ..models import Organization, ApiKey


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'logo', 'plan', 'is_active', 'created_at']
        read_only_fields = ['id', 'plan', 'created_at']


class ApiKeyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key_prefix', 'is_active', 'last_used_at', 'expires_at', 'created_at']
