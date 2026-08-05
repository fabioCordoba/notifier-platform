import pytest
from apps.organizations.models import Organization
from apps.notifications.models import Notification, Recipient, DeliveryAttempt


@pytest.mark.django_db
class TestNotificationModel:
    def setup_method(self):
        self.org = Organization.objects.create(name="Notification Test Org")
        self.notification = Notification.objects.create(
            organization=self.org,
            title="Test Notification",
            message="Hello world",
            channels=["EMAIL"],
        )

    def test_total_recipients_counts_correctly(self):
        assert self.notification.total_recipients == 0
        Recipient.objects.create(notification=self.notification, email="a@test.com")
        Recipient.objects.create(notification=self.notification, email="b@test.com")
        assert self.notification.total_recipients == 2

    def test_delivered_count_only_counts_delivered(self):
        r1 = Recipient.objects.create(notification=self.notification, email="a@test.com")
        r2 = Recipient.objects.create(notification=self.notification, email="b@test.com")
        DeliveryAttempt.objects.create(
            recipient=r1, channel="EMAIL", status=DeliveryAttempt.Status.DELIVERED
        )
        DeliveryAttempt.objects.create(
            recipient=r2, channel="EMAIL", status=DeliveryAttempt.Status.FAILED
        )
        assert self.notification.delivered_count == 1

    def test_str_representation(self):
        assert "Test Notification" in str(self.notification)
        assert "DRAFT" in str(self.notification)

    def test_default_status_is_draft(self):
        assert self.notification.status == Notification.Status.DRAFT

    def test_default_priority_is_normal(self):
        assert self.notification.priority == Notification.Priority.NORMAL


@pytest.mark.django_db
class TestDeliveryAttemptModel:
    def setup_method(self):
        self.org = Organization.objects.create(name="DA Test Org")
        notification = Notification.objects.create(
            organization=self.org, title="DA Test", channels=["EMAIL"]
        )
        self.recipient = Recipient.objects.create(
            notification=notification, email="test@test.com"
        )

    def test_default_status_is_pending(self):
        attempt = DeliveryAttempt.objects.create(
            recipient=self.recipient, channel="EMAIL"
        )
        assert attempt.status == DeliveryAttempt.Status.PENDING

    def test_str_representation(self):
        attempt = DeliveryAttempt.objects.create(
            recipient=self.recipient, channel="EMAIL", status=DeliveryAttempt.Status.SENT
        )
        assert "EMAIL" in str(attempt)
        assert "SENT" in str(attempt)
