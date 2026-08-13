import logging
from django.utils import timezone
from .base import BaseChannel

logger = logging.getLogger(__name__)


class WhatsAppChannel(BaseChannel):
    channel_name = "WHATSAPP"

    def send(self, attempt) -> bool:
        from apps.notifications.models import DeliveryAttempt

        if not attempt.recipient.phone:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "El destinatario no tiene número de teléfono."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        config = self.get_provider_config(attempt)
        if config is None:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "No hay proveedor de WhatsApp activo configurado."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        # attempt.provider is set by get_provider_config to the provider name
        if attempt.provider == "chatwoot":
            from .chatwoot_channel import ChatwootWhatsAppChannel
            return ChatwootWhatsAppChannel()._send_chatwoot(attempt, config)

        notification = attempt.recipient.notification
        body = self._render_body(notification)

        attempt.status = DeliveryAttempt.Status.PROCESSING
        attempt.save(update_fields=["status", "updated_at"])

        try:
            from twilio.rest import Client

            client = Client(config["TWILIO_ACCOUNT_SID"], config["TWILIO_AUTH_TOKEN"])
            from_number = config["TWILIO_FROM_NUMBER"]
            to_number = attempt.recipient.phone

            message = client.messages.create(
                body=body,
                from_=f"whatsapp:{from_number}",
                to=f"whatsapp:{to_number}",
            )
            attempt.status = DeliveryAttempt.Status.SENT
            attempt.sent_at = timezone.now()
            attempt.provider_message_id = message.sid
            attempt.save(update_fields=["status", "sent_at", "provider_message_id", "updated_at"])
            return True

        except Exception as e:
            logger.exception(f"Error enviando WhatsApp via Twilio para attempt {attempt.id}")
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = str(e)
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

    def _render_body(self, notification) -> str:
        if notification.template:
            rendered = notification.template.render(notification.template_variables)
            return rendered.get("body", notification.message)
        return notification.message
