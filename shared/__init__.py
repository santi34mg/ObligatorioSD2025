"""
Módulo compartido para microservicios
Contiene configuración y utilidades comunes
"""

from .rabbitmq_config import RABBITMQ_CONFIG, SystemEvents, SERVICE_CONFIGS
from .rabbitmq_client import RabbitMQClient, EventPublisher, create_rabbitmq_client
from .websocket_client import WebSocketClient, WebSocketServiceIntegration

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
