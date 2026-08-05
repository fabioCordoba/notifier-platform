import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from .base import BaseChannel

logger = logging.getLogger(__name__)


class WebSocketChannel(BaseChannel):
    channel_name = "WEBSOCKET"

    def send(self, attempt) -> bool:
        from apps.notifications.models import DeliveryAttempt

        if not attempt.recipient.app_user_id:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "El destinatario no tiene app_user_id para entrega por WebSocket."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        notification = attempt.recipient.notification
        channel_layer = get_channel_layer()
        group_name = f"org_{notification.organization_id}_user_{attempt.recipient.app_user_id}"

        payload = {
            "type": "notification.send",
            "data": {
                "notification_id": str(notification.id),
                "attempt_id": str(attempt.id),
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "channel": "WEBSOCKET",
                "timestamp": timezone.now().isoformat(),
            }
        }

        try:
            async_to_sync(channel_layer.group_send)(group_name, payload)
            attempt.status = DeliveryAttempt.Status.SENT
            attempt.sent_at = timezone.now()
            attempt.save(update_fields=["status", "sent_at", "updated_at"])
            return True
        except Exception as e:
            logger.exception(f"Error enviando WebSocket para attempt {attempt.id}")
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = str(e)
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False
