import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.organization = self.scope.get('organization')
        self.app_user_id = self.scope.get('app_user_id')

        if not self.organization:
            await self.close(code=4001)
            return

        self.user_group = f"org_{self.organization.id}_user_{self.app_user_id}"
        self.org_group = f"org_{self.organization.id}_broadcast"

        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add(self.org_group, self.channel_name)
        await self.accept()
        logger.info(f"WS connected: org={self.organization.id} user={self.app_user_id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
            await self.channel_layer.group_discard(self.org_group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            if action == 'mark_read':
                await self._mark_attempt_read(data.get('attempt_id'))
                await self.send(json.dumps({
                    'type': 'read_confirmed',
                    'attempt_id': data.get('attempt_id'),
                }))
        except json.JSONDecodeError:
            pass

    async def notification_send(self, event):
        await self.send(json.dumps({
            'type': 'notification',
            'data': event['data'],
        }))

    @database_sync_to_async
    def _mark_attempt_read(self, attempt_id: str):
        from apps.notifications.models import DeliveryAttempt
        from django.utils import timezone
        DeliveryAttempt.objects.filter(id=attempt_id).update(
            status=DeliveryAttempt.Status.READ,
            read_at=timezone.now(),
        )
