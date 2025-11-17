"""
Shared module for microservices
Contains common configuration and utilities
"""

from .rabbitmq_config import RABBITMQ_CONFIG, SystemEvents, SERVICE_CONFIGS
from .rabbitmq_client import RabbitMQClient, EventPublisher, create_rabbitmq_client

# Lazy import for websocket_client to avoid requiring websockets package in all services
def __getattr__(name):
    if name == "WebSocketClient":
        from .websocket_client import WebSocketClient
        return WebSocketClient
    elif name == "WebSocketServiceIntegration":
        from .websocket_client import WebSocketServiceIntegration
        return WebSocketServiceIntegration
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "RABBITMQ_CONFIG",
    "SystemEvents", 
    "SERVICE_CONFIGS",
    "RabbitMQClient",
    "EventPublisher",
    "create_rabbitmq_client",
    "WebSocketClient",
    "WebSocketServiceIntegration"
]
