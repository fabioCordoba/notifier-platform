from .email_channel import EmailChannel
from .sms_channel import SmsChannel
from .whatsapp_channel import WhatsAppChannel
from .push_channel import PushChannel
from .websocket_channel import WebSocketChannel

CHANNEL_REGISTRY = {
    "EMAIL": EmailChannel,
    "SMS": SmsChannel,
    "WHATSAPP": WhatsAppChannel,
    "PUSH": PushChannel,
    "WEBSOCKET": WebSocketChannel,
    "INAPP": WebSocketChannel,
}


def get_channel(channel_name: str):
    cls = CHANNEL_REGISTRY.get(channel_name)
    if cls is None:
        raise ValueError(f"Canal no soportado: {channel_name}")
    return cls()
