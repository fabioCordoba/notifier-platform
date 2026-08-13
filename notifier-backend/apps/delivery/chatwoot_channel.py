import logging
import requests
from django.utils import timezone
from .base import BaseChannel

logger = logging.getLogger(__name__)


class ChatwootWhatsAppChannel(BaseChannel):
    """WhatsApp via Chatwoot API. Used as a delegate from WhatsAppChannel."""
    channel_name = "WHATSAPP"

    def send(self, attempt) -> bool:
        config = self.get_provider_config(attempt)
        if config is None:
            from apps.notifications.models import DeliveryAttempt
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "No hay proveedor Chatwoot activo configurado."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False
        return self._send_chatwoot(attempt, config)

    def _send_chatwoot(self, attempt, config: dict) -> bool:
        from apps.notifications.models import DeliveryAttempt

        if not attempt.recipient.phone:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "El destinatario no tiene número de teléfono."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        notification = attempt.recipient.notification
        body = notification.message or notification.title
        if notification.template:
            rendered = notification.template.render(notification.template_variables)
            body = rendered.get("body", body)

        attempt.status = DeliveryAttempt.Status.PROCESSING
        attempt.save(update_fields=["status", "updated_at"])

        try:
            base_url = config["CHATWOOT_BASE_URL"].rstrip("/")
            account_id = config["CHATWOOT_ACCOUNT_ID"]
            inbox_id = config["CHATWOOT_INBOX_ID"]
            token = config["CHATWOOT_API_TOKEN"]
            headers = {"api_access_token": token, "Content-Type": "application/json"}

            phone = attempt.recipient.phone
            name = attempt.recipient.name or phone

            contact_id = self._find_or_create_contact(base_url, account_id, headers, phone, name)
            conversation_id = self._get_or_create_conversation(base_url, account_id, inbox_id, headers, contact_id)
            message_id = self._send_message(base_url, account_id, headers, conversation_id, body)

            attempt.status = DeliveryAttempt.Status.SENT
            attempt.sent_at = timezone.now()
            attempt.provider_message_id = str(message_id)
            attempt.save(update_fields=["status", "sent_at", "provider_message_id", "updated_at"])
            return True

        except Exception as e:
            logger.exception(f"Error enviando WhatsApp via Chatwoot para attempt {attempt.id}")
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = str(e)
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

    def _find_or_create_contact(self, base_url, account_id, headers, phone, name) -> int:
        r = requests.get(
            f"{base_url}/api/v1/accounts/{account_id}/contacts/search",
            headers=headers,
            params={"q": phone, "include_contacts": True},
            timeout=10,
        )
        r.raise_for_status()
        contacts = r.json().get("payload", {}).get("contacts", [])
        if contacts:
            return contacts[0]["id"]

        r = requests.post(
            f"{base_url}/api/v1/accounts/{account_id}/contacts",
            headers=headers,
            json={"phone_number": phone, "name": name},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["id"]

    def _get_or_create_conversation(self, base_url, account_id, inbox_id, headers, contact_id) -> int:
        r = requests.get(
            f"{base_url}/api/v1/accounts/{account_id}/contacts/{contact_id}/conversations",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        conversations = r.json().get("payload", [])

        for conv in conversations:
            if str(conv.get("inbox_id")) == str(inbox_id) and conv.get("status") == "open":
                return conv["id"]

        r = requests.post(
            f"{base_url}/api/v1/accounts/{account_id}/conversations",
            headers=headers,
            json={"contact_id": contact_id, "inbox_id": int(inbox_id)},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["id"]

    def _send_message(self, base_url, account_id, headers, conversation_id, body) -> int:
        r = requests.post(
            f"{base_url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": body, "message_type": "outgoing", "private": False},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["id"]
