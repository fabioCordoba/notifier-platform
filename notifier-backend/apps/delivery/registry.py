from .email_channel import EmailChannel
from .websocket_channel import WebSocketChannel

CHANNEL_REGISTRY = {
    "EMAIL": EmailChannel,
    "WEBSOCKET": WebSocketChannel,
    "INAPP": WebSocketChannel,
}


def get_channel(channel_name: str):
    cls = CHANNEL_REGISTRY.get(channel_name)
    if cls is None:
        raise ValueError(f"Canal no soportado: {channel_name}")
    return cls()
