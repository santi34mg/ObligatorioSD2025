"""
Cliente RabbitMQ compartido para todos los microservicios
Implementa patrones Publisher/Subscriber y Message Queue
"""
import json
import asyncio
import logging
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from .rabbitmq_config import RABBITMQ_CONFIG, SystemEvents, SERVICE_CONFIGS

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """RabbitMQ Client for asynchronous communication between microservices"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.rabbitmq_url = RABBITMQ_CONFIG["url"]
        self.consumers: Dict[str, asyncio.Task] = {}
        
    async def connect(self):
        """Conectar a RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                self.rabbitmq_url,
                client_properties={
                    "service_name": self.service_name,
                    "connected_at": datetime.now().isoformat()
                }
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            
            # Configurar exchanges
            await self._setup_exchanges()
            
            logger.info(f"{self.service_name} conectado a RabbitMQ")
        except Exception as e:
            logger.error(f"Error conectando {self.service_name} a RabbitMQ: {e}")
            raise

    async def _setup_exchanges(self):
        """Configurar todos los exchanges necesarios"""
        for exchange_name, exchange_config in RABBITMQ_CONFIG["exchanges"].items():
            exchange = await self.channel.declare_exchange(
                exchange_config["name"],
                ExchangeType.TOPIC,
                durable=exchange_config["durable"]
            )
            logger.debug(f"Exchange '{exchange_config['name']}' configurado")

    async def disconnect(self):
        """Desconectar de RabbitMQ"""
        # Cancelar todos los consumers
        for consumer_name, task in self.consumers.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info(f"{self.service_name} desconectado de RabbitMQ")

    async def publish_event(self, event_type: str, data: Dict[str, Any], routing_key: Optional[str] = None):
        """Publicar evento en RabbitMQ"""
        if not self.channel:
            await self.connect()
        
        # Encontrar el exchange correcto basado en el tipo de evento
        exchange_name = self._get_exchange_for_event(event_type)
        exchange = await self.channel.declare_exchange(
            exchange_name,
            ExchangeType.TOPIC,
            durable=True
        )
        
        # Crear mensaje
        message_data = {
            "event_type": event_type,
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "version": "1.0"
        }
        
        message_body = json.dumps(message_data).encode()
        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT,
            headers={
                "service": self.service_name,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Usar routing_key personalizado o el por defecto
        final_routing_key = routing_key or event_type
        
        # Publicar mensaje
        await exchange.publish(message, routing_key=final_routing_key)
        
        logger.info(f"{self.service_name} published event '{event_type}': {data}")

    async def consume_events(self, event_types: List[str], callback: Callable):
        """Consume specific events"""
        if not self.channel:
            await self.connect()
        
        # Configurar queues para los eventos
        for event_type in event_types:
            queue_config = self._get_queue_config_for_event(event_type)
            
            # Declarar queue
            queue = await self.channel.declare_queue(
                queue_config["name"],
                durable=queue_config["durable"]
            )
            
            # Declarar exchange
            exchange = await self.channel.declare_exchange(
                queue_config["exchange"],
                ExchangeType.TOPIC,
                durable=True
            )
            
            # Bind queue al exchange
            await queue.bind(exchange, queue_config["routing_key"])
            
            # Configurar consumer
            consumer_name = f"{self.service_name}_{event_type}_consumer"
            task = asyncio.create_task(
                self._consume_messages(queue, callback, event_type)
            )
            self.consumers[consumer_name] = task
            
            logger.info(f"{self.service_name} escuchando eventos '{event_type}' en queue '{queue_config['name']}'")

    async def _consume_messages(self, queue, callback: Callable, event_type: str):
        """Consume messages from a specific queue"""
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        # Decodificar mensaje
                        message_data = json.loads(message.body.decode())
                        
                        logger.info(f"{self.service_name} procesando evento '{event_type}': {message_data.get('data', {})}")
                        
                        # Llamar callback
                        await callback(event_type, message_data)
                        
                    except Exception as e:
                        logger.error(f"Error procesando mensaje en {self.service_name}: {e}")
                        

    def _get_exchange_for_event(self, event_type: str) -> str:
        """Get the correct exchange for an event type"""
        if event_type.startswith("user."):
            return "user.events"
        elif event_type.startswith("content."):
            return "content.events"
        elif event_type.startswith("collaboration."):
            return "collaboration.events"
        elif event_type.startswith("message.") or event_type.startswith("chat."):
            return "communication.events"
        elif event_type.startswith("moderation."):
            return "moderation.events"
        else:
            return "user.events"  # Default

    def _get_queue_config_for_event(self, event_type: str) -> Dict:
        """Get queue configuration for an event type"""
        queue_key = event_type.replace(".", "_")
        if queue_key in RABBITMQ_CONFIG["queues"]:
            return RABBITMQ_CONFIG["queues"][queue_key]
        else:
            # Queue por defecto
            return {
                "name": f"{event_type.replace('.', '_')}.queue",
                "exchange": self._get_exchange_for_event(event_type),
                "routing_key": event_type,
                "durable": True
            }

# Utility functions for specific events
class EventPublisher:
    """Helper class to publish common events"""
    
    def __init__(self, client: RabbitMQClient):
        self.client = client
    
    async def publish_event(self, event_type: str, data: Dict[str, Any], routing_key: Optional[str] = None):
        """Publish generic event"""
        await self.client.publish_event(event_type, data, routing_key)
    
    async def publish_user_registered(self, user_data: Dict[str, Any]):
        """Publicar evento de usuario registrado"""
        await self.client.publish_event(SystemEvents.USER_REGISTERED, user_data)
    
    async def publish_user_login(self, user_data: Dict[str, Any]):
        """Publicar evento de usuario logueado"""
        await self.client.publish_event(SystemEvents.USER_LOGIN, user_data)
    
    async def publish_content_created(self, content_data: Dict[str, Any]):
        """Publicar evento de contenido creado"""
        await self.client.publish_event(SystemEvents.CONTENT_CREATED, content_data)
    
    async def publish_message_sent(self, message_data: Dict[str, Any]):
        """Publicar evento de mensaje enviado"""
        await self.client.publish_event(SystemEvents.MESSAGE_SENT, message_data)
    
    async def publish_moderation_review(self, review_data: Dict[str, Any]):
        """Publish moderation review event"""
        await self.client.publish_event(SystemEvents.MODERATION_REVIEW, review_data)

# Factory function to create clients
def create_rabbitmq_client(service_name: str) -> RabbitMQClient:
    """Create RabbitMQ client for a specific service"""
    return RabbitMQClient(service_name)
