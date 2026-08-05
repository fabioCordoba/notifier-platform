import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils import timezone
from .base import BaseChannel

logger = logging.getLogger(__name__)


class EmailChannel(BaseChannel):
    channel_name = "EMAIL"

    def send(self, attempt) -> bool:
        from apps.notifications.models import DeliveryAttempt
        if not attempt.recipient.email:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "El destinatario no tiene direccion de email."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        config = self.get_provider_config(attempt)
        if config is None:
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = "No hay proveedor de email activo configurado."
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

        notification = attempt.recipient.notification
        rendered = self._render_content(notification)
        attempt.status = DeliveryAttempt.Status.PROCESSING
        attempt.save(update_fields=["status", "updated_at"])

        try:
            if attempt.provider == "sendgrid":
                return self._send_via_sendgrid(attempt, config, rendered)
            elif attempt.provider == "smtp":
                return self._send_via_smtp(attempt, config, rendered)
            else:
                raise ValueError(f"Proveedor desconocido: {attempt.provider}")
        except Exception as e:
            logger.exception(f"Error enviando email para attempt {attempt.id}")
            attempt.status = DeliveryAttempt.Status.FAILED
            attempt.error_message = str(e)
            attempt.save(update_fields=["status", "error_message", "updated_at"])
            return False

    def _render_content(self, notification) -> dict:
        if notification.template:
            return notification.template.render(notification.template_variables)
        return {"subject": notification.title, "body": notification.message}

    def _send_via_sendgrid(self, attempt, config, rendered) -> bool:
        import sendgrid as sg_module
        from sendgrid.helpers.mail import Mail
        from apps.notifications.models import DeliveryAttempt

        sg = sg_module.SendGridAPIClient(api_key=config["api_key"])
        mail = Mail(
            from_email=config.get("from_email", "no-reply@notifier.io"),
            to_emails=attempt.recipient.email,
            subject=rendered["subject"],
            html_content=rendered["body"],
        )
        response = sg.send(mail)
        if response.status_code in (200, 202):
            attempt.status = DeliveryAttempt.Status.SENT
            attempt.sent_at = timezone.now()
            attempt.provider_message_id = response.headers.get("X-Message-Id", "")
            attempt.save(update_fields=["status", "sent_at", "provider_message_id", "updated_at"])
            return True
        attempt.status = DeliveryAttempt.Status.FAILED
        attempt.error_message = f"SendGrid respondio con codigo {response.status_code}"
        attempt.save(update_fields=["status", "error_message", "updated_at"])
        return False

    def _send_via_smtp(self, attempt, config, rendered) -> bool:
        from apps.notifications.models import DeliveryAttempt

        msg = MIMEMultipart("alternative")
        msg["Subject"] = rendered["subject"]
        msg["From"] = config.get("from_email", "no-reply@notifier.io")
        msg["To"] = attempt.recipient.email
        msg.attach(MIMEText(rendered["body"], "html"))

        with smtplib.SMTP(config["host"], config.get("port", 587)) as server:
            server.starttls()
            server.login(config["username"], config["password"])
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())

        attempt.status = DeliveryAttempt.Status.SENT
        attempt.sent_at = timezone.now()
        attempt.save(update_fields=["status", "sent_at", "updated_at"])
        return True
