import pytest
from unittest.mock import patch, MagicMock
from apps.organizations.models import Organization
from apps.notifications.models import Notification, Recipient, DeliveryAttempt
from apps.notifications.tasks import (
    process_notification,
    send_email_task,
    send_websocket_task,
    _update_notification_status,
)


@pytest.fixture
def org(db):
    return Organization.objects.create(name="Tasks Test Org")


@pytest.fixture
def notification_with_recipients(org):
    n = Notification.objects.create(
        organization=org, title="Task Test", message="Hello",
        channels=["EMAIL", "WEBSOCKET"], status=Notification.Status.QUEUED
    )
    r1 = Recipient.objects.create(notification=n, email="a@test.com", app_user_id="user-1")
    r2 = Recipient.objects.create(notification=n, email="b@test.com", app_user_id="user-2")
    return n, [r1, r2]


@pytest.mark.django_db
class TestProcessNotification:
    @patch("apps.notifications.tasks.send_email_task.delay")
    @patch("apps.notifications.tasks.send_websocket_task.delay")
    def test_creates_delivery_attempts_per_recipient_per_channel(
        self, mock_ws, mock_email, notification_with_recipients
    ):
        n, recipients = notification_with_recipients
        process_notification(str(n.id))

        total_attempts = DeliveryAttempt.objects.filter(
            recipient__notification=n
        ).count()
        assert total_attempts == 4  # 2 recipients × 2 channels

    @patch("apps.notifications.tasks.send_email_task.delay")
    @patch("apps.notifications.tasks.send_websocket_task.delay")
    def test_dispatches_email_tasks(self, mock_ws, mock_email, notification_with_recipients):
        n, _ = notification_with_recipients
        process_notification(str(n.id))
        assert mock_email.call_count == 2  # one per recipient

    @patch("apps.notifications.tasks.send_email_task.delay")
    @patch("apps.notifications.tasks.send_websocket_task.delay")
    def test_dispatches_websocket_tasks(self, mock_ws, mock_email, notification_with_recipients):
        n, _ = notification_with_recipients
        process_notification(str(n.id))
        assert mock_ws.call_count == 2

    @patch("apps.notifications.tasks.send_email_task.delay")
    @patch("apps.notifications.tasks.send_websocket_task.delay")
    def test_sets_notification_to_processing(self, mock_ws, mock_email, notification_with_recipients):
        n, _ = notification_with_recipients
        process_notification(str(n.id))
        n.refresh_from_db()
        assert n.status == Notification.Status.PROCESSING

    def test_does_not_fail_for_nonexistent_notification(self):
        import uuid
        process_notification(str(uuid.uuid4()))


@pytest.mark.django_db
class TestUpdateNotificationStatus:
    def test_all_delivered_sets_completed(self, org):
        n = Notification.objects.create(
            organization=org, title="Status Test", channels=["EMAIL"],
            status=Notification.Status.PROCESSING
        )
        r = Recipient.objects.create(notification=n, email="test@test.com")
        DeliveryAttempt.objects.create(recipient=r, channel="EMAIL", status=DeliveryAttempt.Status.DELIVERED)

        _update_notification_status(str(n.id))
        n.refresh_from_db()
        assert n.status == Notification.Status.COMPLETED

    def test_all_failed_sets_failed(self, org):
        n = Notification.objects.create(
            organization=org, title="Failed Test", channels=["EMAIL"],
            status=Notification.Status.PROCESSING
        )
        r = Recipient.objects.create(notification=n, email="test@test.com")
        DeliveryAttempt.objects.create(recipient=r, channel="EMAIL", status=DeliveryAttempt.Status.FAILED)

        _update_notification_status(str(n.id))
        n.refresh_from_db()
        assert n.status == Notification.Status.FAILED

    def test_mixed_sets_partially_failed(self, org):
        n = Notification.objects.create(
            organization=org, title="Mixed Test", channels=["EMAIL"],
            status=Notification.Status.PROCESSING
        )
        r1 = Recipient.objects.create(notification=n, email="a@test.com")
        r2 = Recipient.objects.create(notification=n, email="b@test.com")
        DeliveryAttempt.objects.create(recipient=r1, channel="EMAIL", status=DeliveryAttempt.Status.SENT)
        DeliveryAttempt.objects.create(recipient=r2, channel="EMAIL", status=DeliveryAttempt.Status.FAILED)

        _update_notification_status(str(n.id))
        n.refresh_from_db()
        assert n.status == Notification.Status.PARTIALLY_FAILED

    def test_pending_attempts_do_not_change_status(self, org):
        n = Notification.objects.create(
            organization=org, title="Pending Test", channels=["EMAIL"],
            status=Notification.Status.PROCESSING
        )
        r = Recipient.objects.create(notification=n, email="test@test.com")
        DeliveryAttempt.objects.create(recipient=r, channel="EMAIL", status=DeliveryAttempt.Status.QUEUED)

        _update_notification_status(str(n.id))
        n.refresh_from_db()
        assert n.status == Notification.Status.PROCESSING


@pytest.mark.django_db
class TestSendEmailTask:
    @patch("apps.delivery.registry.EmailChannel.send")
    def test_calls_email_channel_send(self, mock_send, org):
        mock_send.return_value = True
        n = Notification.objects.create(
            organization=org, title="Email Task", message="Test", channels=["EMAIL"]
        )
        r = Recipient.objects.create(notification=n, email="test@test.com")
        attempt = DeliveryAttempt.objects.create(
            recipient=r, channel="EMAIL", status=DeliveryAttempt.Status.QUEUED
        )
        send_email_task(str(attempt.id))
        mock_send.assert_called_once()
