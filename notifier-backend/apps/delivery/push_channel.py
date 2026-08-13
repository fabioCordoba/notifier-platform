import logging
from django.utils import timezone
from .base import BaseChannel

logger = logging.getLogger(__name__)


def _get_firebase_app(config: dict):
    import firebase_admin
    from firebase_admin import credentials

    app_name = f"org_{config.get('project_id', 'default')}"
    try:
        return firebase_admin.get_app(app_name)
    except ValueError:
        cred = credentials.Certificate(config)
        return firebase_admin.initialize_app(cred, name=app_name)


class PushChannel(BaseChannel):
    channel_name = "PUSH"

    def send(self, attempt) -> bool:
        from apps.notifications.models import DeliveryAttempt

        if not attempt.recipient.push_token:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "El destinatario no tiene push token registrado."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        config = self.get_provider_config(attempt)
        if config is None:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "No hay proveedor de Push activo configurado."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        notification = attempt.recipient.notification

        attempt.status = DeliveryAttempt.Status.PROCESSING
        attempt.save(update_fields=["status", "updated_at"])

        try:
            from firebase_admin import messaging

            app = _get_firebase_app(config)
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.message,
                ),
                token=attempt.recipient.push_token,
                data={k: str(v) for k, v in (notification.metadata or {}).items()},
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound="default")
                    )
                ),
            )
            response = messaging.send(message, app=app)
            attempt.status = DeliveryAttempt.Status.SENT
            attempt.sent_at = timezone.now()
            attempt.provider_message_id = response
            attempt.save(update_fields=["status", "sent_at", "provider_message_id", "updated_at"])
            return True

        except Exception as e:
            logger.exception(f"Error enviando Push para attempt {attempt.id}")
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = str(e)
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False
