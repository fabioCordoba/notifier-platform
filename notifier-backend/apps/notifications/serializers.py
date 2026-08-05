from rest_framework import serializers
from .models import Notification, Recipient, DeliveryAttempt


class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = ["id", "name", "email", "phone", "app_user_id", "push_token", "metadata"]


class DeliveryAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAttempt
        fields = [
            "id", "channel", "provider", "status",
            "error_message", "attempt_number",
            "sent_at", "delivered_at", "read_at", "created_at",
        ]


class RecipientDetailSerializer(RecipientSerializer):
    delivery_attempts = DeliveryAttemptSerializer(many=True, read_only=True)

    class Meta(RecipientSerializer.Meta):
        fields = RecipientSerializer.Meta.fields + ["delivery_attempts"]


class NotificationSendSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    message = serializers.CharField(required=False, allow_blank=True)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    template_variables = serializers.DictField(required=False, default=dict)
    priority = serializers.ChoiceField(
        choices=Notification.Priority.choices,
        default=Notification.Priority.NORMAL,
    )
    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=DeliveryAttempt.Channel.choices),
        default=["EMAIL"],
    )
    recipients = RecipientSerializer(many=True)
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False, default=dict)

    def validate(self, data):
        if not data.get("message") and not data.get("template_id"):
            raise serializers.ValidationError(
                "Se requiere 'message' o 'template_id'."
            )
        if not data.get("recipients"):
            raise serializers.ValidationError("Se requiere al menos un destinatario.")
        return data


class NotificationDetailSerializer(serializers.ModelSerializer):
    recipients = RecipientDetailSerializer(many=True, read_only=True)
    total_recipients = serializers.IntegerField(read_only=True)
    delivered_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "title", "message", "priority", "status", "channels",
            "template", "template_variables", "metadata",
            "scheduled_at", "created_at", "updated_at",
            "total_recipients", "delivered_count", "recipients",
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    total_recipients = serializers.IntegerField(read_only=True)
    delivered_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id", "title", "priority", "status", "channels",
            "scheduled_at", "created_at",
            "total_recipients", "delivered_count",
        ]
