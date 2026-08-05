import pytest
from unittest.mock import MagicMock, patch
from apps.organizations.models import Organization
from apps.notifications.models import Notification, Recipient, DeliveryAttempt
from apps.delivery.email_channel import EmailChannel


@pytest.fixture
def setup_attempt(db, settings):
    settings.FIELD_ENCRYPTION_KEY = "dGhpcy1pcy1hLXRlc3Qta2V5LWZvci11bml0LXRlc3Q="
    org = Organization.objects.create(name="Email Channel Test Org")
    notification = Notification.objects.create(
        organization=org, title="Test Email", message="<p>Hola</p>", channels=["EMAIL"]
    )
    recipient = Recipient.objects.create(notification=notification, email="test@test.com")
    attempt = DeliveryAttempt.objects.create(
        recipient=recipient, channel="EMAIL", status=DeliveryAttempt.Status.QUEUED
    )
    return attempt, org


@pytest.mark.django_db
class TestEmailChannel:
    def test_send_fails_without_email(self, db):
        org = Organization.objects.create(name="No Email Org")
        n = Notification.objects.create(organization=org, title="T", message="M", channels=["EMAIL"])
        r = Recipient.objects.create(notification=n, name="Sin Email")
        attempt = DeliveryAttempt.objects.create(recipient=r, channel="EMAIL")

        channel = EmailChannel()
        result = channel.send(attempt)

        assert result is False
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.FAILED
        assert "email" in attempt.error_message.lower()

    def test_send_fails_without_provider(self, setup_attempt):
        attempt, org = setup_attempt
        channel = EmailChannel()
        result = channel.send(attempt)

        assert result is False
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.FAILED
        assert "proveedor" in attempt.error_message.lower()

    @patch("apps.delivery.email_channel.smtplib.SMTP")
    def test_send_via_smtp_success(self, mock_smtp_cls, setup_attempt):
        attempt, org = setup_attempt
        from apps.providers.models import Provider
        from cryptography.fernet import Fernet
        import json

        key = Fernet.generate_key()
        from django.test import override_settings
        with override_settings(FIELD_ENCRYPTION_KEY=key.decode()):
            provider = Provider(
                organization=org,
                channel=Provider.Channel.EMAIL,
                name=Provider.Name.SMTP,
                is_active=True,
                is_default=True,
            )
            provider.set_config({
                "host": "smtp.test.com",
                "port": 587,
                "username": "user",
                "password": "pass",
                "from_email": "no-reply@test.com",
            })
            provider.save()

            mock_server = MagicMock()
            mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

            channel = EmailChannel()
            result = channel.send(attempt)

        assert result is True
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.SENT
        assert attempt.sent_at is not None

    @patch("apps.delivery.email_channel.smtplib.SMTP")
    def test_send_via_smtp_failure_marks_failed(self, mock_smtp_cls, setup_attempt):
        attempt, org = setup_attempt
        from apps.providers.models import Provider
        from cryptography.fernet import Fernet
        from django.test import override_settings

        with override_settings(FIELD_ENCRYPTION_KEY=Fernet.generate_key().decode()):
            provider = Provider(
                organization=org,
                channel=Provider.Channel.EMAIL,
                name=Provider.Name.SMTP,
                is_active=True,
                is_default=True,
            )
            provider.set_config({
                "host": "smtp.test.com",
                "port": 587,
                "username": "user",
                "password": "pass",
            })
            provider.save()

            mock_smtp_cls.side_effect = Exception("Connection refused")
            channel = EmailChannel()
            result = channel.send(attempt)

        assert result is False
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.FAILED
        assert "Connection refused" in attempt.error_message
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.FAILED
        assert "Connection refused" in attempt.error_message
