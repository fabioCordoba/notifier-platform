import pytest
from rest_framework.test import APIClient
from apps.organizations.models import Organization, ApiKey
from apps.notifications.models import Notification, Recipient


@pytest.fixture
def org_with_key(db):
    org = Organization.objects.create(name="API Test Org")
    _, raw_key = ApiKey.generate(org, "Test Key")
    return org, raw_key


@pytest.fixture
def auth_client(org_with_key):
    org, raw_key = org_with_key
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Api-Key {raw_key}")
    return client, org


@pytest.mark.django_db
class TestNotificationSendView:
    def test_send_without_auth_returns_403(self):
        client = APIClient()
        response = client.post("/api/v1/notifications/send/", {})
        assert response.status_code in (401, 403)

    def test_send_valid_payload_returns_202(self, auth_client, mocker):
        client, org = auth_client
        mocker.patch("apps.notifications.tasks.process_notification.delay")
        payload = {
            "title": "Hola",
            "message": "Mensaje de prueba",
            "channels": ["EMAIL"],
            "recipients": [{"email": "test@example.com", "name": "Test User"}],
        }
        response = client.post("/api/v1/notifications/send/", payload, format="json")
        assert response.status_code == 202
        assert Notification.objects.filter(organization=org).count() == 1

    def test_send_creates_recipients(self, auth_client, mocker):
        client, org = auth_client
        mocker.patch("apps.notifications.tasks.process_notification.delay")
        payload = {
            "title": "Multi recipient",
            "message": "Test",
            "channels": ["EMAIL"],
            "recipients": [
                {"email": "a@test.com"},
                {"email": "b@test.com"},
            ],
        }
        response = client.post("/api/v1/notifications/send/", payload, format="json")
        assert response.status_code == 202
        notification = Notification.objects.get(organization=org)
        assert notification.recipients.count() == 2

    def test_send_without_message_and_template_returns_400(self, auth_client):
        client, org = auth_client
        payload = {
            "title": "Sin contenido",
            "channels": ["EMAIL"],
            "recipients": [{"email": "test@test.com"}],
        }
        response = client.post("/api/v1/notifications/send/", payload, format="json")
        assert response.status_code == 400

    def test_send_dispatches_celery_task(self, auth_client, mocker):
        client, org = auth_client
        mock_delay = mocker.patch("apps.notifications.tasks.process_notification.delay")
        payload = {
            "title": "Task Test",
            "message": "Test",
            "channels": ["EMAIL"],
            "recipients": [{"email": "test@test.com"}],
        }
        client.post("/api/v1/notifications/send/", payload, format="json")
        mock_delay.assert_called_once()

    def test_scheduled_notification_does_not_dispatch_immediately(self, auth_client, mocker):
        client, org = auth_client
        mock_delay = mocker.patch("apps.notifications.tasks.process_notification.delay")
        payload = {
            "title": "Scheduled",
            "message": "Test",
            "channels": ["EMAIL"],
            "recipients": [{"email": "test@test.com"}],
            "scheduled_at": "2030-01-01T12:00:00Z",
        }
        client.post("/api/v1/notifications/send/", payload, format="json")
        mock_delay.assert_not_called()


@pytest.mark.django_db
class TestNotificationDetailView:
    def test_get_own_notification(self, auth_client, mocker):
        client, org = auth_client
        mocker.patch("apps.notifications.tasks.process_notification.delay")
        n = Notification.objects.create(
            organization=org, title="Detail Test", channels=["EMAIL"]
        )
        response = client.get(f"/api/v1/notifications/{n.id}/")
        assert response.status_code == 200
        assert response.data["title"] == "Detail Test"

    def test_cannot_access_other_orgs_notification(self, auth_client, db):
        client, org = auth_client
        other_org = Organization.objects.create(name="Other Org")
        n = Notification.objects.create(
            organization=other_org, title="Private", channels=["EMAIL"]
        )
        response = client.get(f"/api/v1/notifications/{n.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestNotificationRetryView:
    def test_retry_failed_notification(self, auth_client, mocker):
        client, org = auth_client
        mock_delay = mocker.patch("apps.notifications.tasks.process_notification.delay")
        n = Notification.objects.create(
            organization=org, title="Retry Me", status=Notification.Status.FAILED,
            channels=["EMAIL"]
        )
        response = client.post(f"/api/v1/notifications/{n.id}/retry/")
        assert response.status_code == 202
        mock_delay.assert_called_once_with(str(n.id))

    def test_retry_processing_notification_returns_400(self, auth_client):
        client, org = auth_client
        n = Notification.objects.create(
            organization=org, title="Processing", status=Notification.Status.PROCESSING,
            channels=["EMAIL"]
        )
        response = client.post(f"/api/v1/notifications/{n.id}/retry/")
        assert response.status_code == 400
