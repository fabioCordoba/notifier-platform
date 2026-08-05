from rest_framework import serializers
from .models import Template


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'channel', 'subject', 'body',
            'variables', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user
        return super().create(validated_data)
