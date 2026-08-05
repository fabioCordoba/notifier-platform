import pytest
from unittest.mock import patch, MagicMock
from apps.organizations.models import Organization
from apps.notifications.models import Notification, Recipient, DeliveryAttempt
from apps.delivery.websocket_channel import WebSocketChannel


@pytest.fixture
def ws_attempt(db):
    org = Organization.objects.create(name="WS Channel Test Org")
    notification = Notification.objects.create(
        organization=org, title="WS Test", message="Hello WS", channels=["WEBSOCKET"]
    )
    recipient = Recipient.objects.create(
        notification=notification, app_user_id="user-abc-123"
    )
    attempt = DeliveryAttempt.objects.create(
        recipient=recipient, channel="WEBSOCKET", status=DeliveryAttempt.Status.QUEUED
    )
    return attempt, org


@pytest.mark.django_db
class TestWebSocketChannel:
    def test_send_fails_without_app_user_id(self, db):
        org = Organization.objects.create(name="No UserId Org")
        n = Notification.objects.create(organization=org, title="T", message="M", channels=["WEBSOCKET"])
        r = Recipient.objects.create(notification=n)
        attempt = DeliveryAttempt.objects.create(recipient=r, channel="WEBSOCKET")

        channel = WebSocketChannel()
        result = channel.send(attempt)

        assert result is False
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.FAILED
        assert "app_user_id" in attempt.error_message

    @patch("apps.delivery.websocket_channel.get_channel_layer")
    @patch("apps.delivery.websocket_channel.async_to_sync")
    def test_send_calls_correct_group(self, mock_async_to_sync, mock_get_layer, ws_attempt):
        attempt, org = ws_attempt
        mock_layer = MagicMock()
        mock_get_layer.return_value = mock_layer
        mock_group_send = MagicMock()
        mock_async_to_sync.return_value = mock_group_send

        channel = WebSocketChannel()
        result = channel.send(attempt)

        assert result is True
        expected_group = f"org_{org.id}_user_user-abc-123"
        mock_group_send.assert_called_once()
        call_args = mock_group_send.call_args[0]
        assert call_args[0] == expected_group

    @patch("apps.delivery.websocket_channel.get_channel_layer")
    @patch("apps.delivery.websocket_channel.async_to_sync")
    def test_send_marks_attempt_sent(self, mock_async_to_sync, mock_get_layer, ws_attempt):
        attempt, org = ws_attempt
        mock_get_layer.return_value = MagicMock()
        mock_async_to_sync.return_value = MagicMock()

        channel = WebSocketChannel()
        channel.send(attempt)

        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.SENT
        assert attempt.sent_at is not None

    @patch("apps.delivery.websocket_channel.get_channel_layer")
    @patch("apps.delivery.websocket_channel.async_to_sync")
    def test_send_marks_failed_on_exception(self, mock_async_to_sync, mock_get_layer, ws_attempt):
        attempt, org = ws_attempt
        mock_get_layer.return_value = MagicMock()
        mock_async_to_sync.return_value = MagicMock(side_effect=Exception("Redis down"))

        channel = WebSocketChannel()
        result = channel.send(attempt)

        assert result is False
        attempt.refresh_from_db()
        assert attempt.status == DeliveryAttempt.Status.FAILED
        assert "Redis down" in attempt.error_message
