from abc import ABC, abstractmethod
from typing import Optional


class BaseChannel(ABC):
    channel_name: str = None

    @abstractmethod
    def send(self, attempt) -> bool:
        raise NotImplementedError

    def get_provider_config(self, attempt) -> Optional[dict]:
        from apps.providers.models import Provider
        try:
            provider = Provider.objects.get(
                organization=attempt.recipient.notification.organization,
                channel=self.channel_name,
                is_default=True,
                is_active=True,
            )
            attempt.provider = provider.name
            attempt.save(update_fields=['provider'])
            return provider.get_config()
        except Provider.DoesNotExist:
            return None
