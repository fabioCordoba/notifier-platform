import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from apps.organizations.models import Organization, ApiKey
from apps.notifications.models import Notification, Recipient, DeliveryAttempt


@pytest.fixture
def org_with_key(db):
    org = Organization.objects.create(name="WS Consumer Test Org")
    _, raw_key = ApiKey.generate(org, "WS Key")
    return org, raw_key


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestNotificationConsumer:
    async def test_connect_without_api_key_closes_with_4001(self):
        from config.asgi import application
        communicator = WebsocketCommunicator(application, "/ws/notifications/")
        connected, code = await communicator.connect()
        assert not connected or code == 4001
        await communicator.disconnect()

    async def test_connect_with_valid_api_key_succeeds(self, org_with_key):
        from config.asgi import application
        org, raw_key = org_with_key
        url = f"/ws/notifications/?api_key={raw_key}&user_id=test-user"
        communicator = WebsocketCommunicator(application, url)
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    async def test_notification_received_via_channel_layer(self, org_with_key):
        from config.asgi import application
        org, raw_key = org_with_key
        url = f"/ws/notifications/?api_key={raw_key}&user_id=test-user-recv"
        communicator = WebsocketCommunicator(application, url)
        connected, _ = await communicator.connect()
        assert connected

        channel_layer = get_channel_layer()
        group_name = f"org_{org.id}_user_test-user-recv"
        await channel_layer.group_send(group_name, {
            "type": "notification.send",
            "data": {
                "notification_id": "test-id",
                "title": "Test Notification",
                "message": "Hello",
                "priority": "NORMAL",
                "channel": "WEBSOCKET",
                "timestamp": "2024-01-01T00:00:00",
            }
        })

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "notification"
        assert response["data"]["title"] == "Test Notification"
        await communicator.disconnect()

    async def test_mark_read_updates_attempt_status(self, org_with_key):
        from channels.db import database_sync_to_async
        from config.asgi import application
        org, raw_key = org_with_key

        @database_sync_to_async
        def create_attempt():
            n = Notification.objects.create(
                organization=org, title="Read Test", message="Test", channels=["WEBSOCKET"]
            )
            r = Recipient.objects.create(notification=n, app_user_id="mark-read-user")
            return DeliveryAttempt.objects.create(
                recipient=r, channel="WEBSOCKET", status=DeliveryAttempt.Status.SENT
            )

        @database_sync_to_async
        def get_attempt_status(attempt_id):
            return DeliveryAttempt.objects.get(id=attempt_id).status

        attempt = await create_attempt()
        url = f"/ws/notifications/?api_key={raw_key}&user_id=mark-read-user"
        communicator = WebsocketCommunicator(application, url)
        connected, _ = await communicator.connect()
        assert connected

        await communicator.send_json_to({
            "action": "mark_read",
            "attempt_id": str(attempt.id),
        })

        response = await communicator.receive_json_from(timeout=2)
        assert response["type"] == "read_confirmed"

        db_status = await get_attempt_status(attempt.id)
        assert db_status == DeliveryAttempt.Status.READ
        await communicator.disconnect()
