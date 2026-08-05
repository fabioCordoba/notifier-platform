from rest_framework import serializers
from .models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    config = serializers.DictField(write_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'channel', 'name', 'config', 'is_active', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        config = validated_data.pop('config')
        validated_data['organization'] = self.context['request'].user
        provider = Provider(**validated_data)
        provider.set_config(config)
        provider.save()
        return provider

    def update(self, instance, validated_data):
        config = validated_data.pop('config', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if config is not None:
            instance.set_config(config)
        instance.save()
        return instance
