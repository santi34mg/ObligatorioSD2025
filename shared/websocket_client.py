"""
Cliente WebSocket compartido para microservicios
Permite a otros microservicios comunicarse con el WebSocket service
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

class WebSocketClient:
    """Cliente para comunicarse con el WebSocket service"""
    
    def __init__(self, websocket_service_url: str = "ws://websocket-service:8000"):
        self.websocket_service_url = websocket_service_url
        self.connection = None
        self.service_id = None
    
    async def connect(self, service_id: str):
        """Conectar al WebSocket service como microservicio"""
        try:
            self.service_id = service_id
            self.connection = await websockets.connect(
                f"{self.websocket_service_url}/ws/{service_id}"
            )
            logger.info(f"Microservicio {service_id} conectado al WebSocket service")
            return True
        except Exception as e:
            logger.error(f"Error conectando al WebSocket service: {e}")
            return False
    
    async def disconnect(self):
        """Desconectar del WebSocket service"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info(f"Microservicio {self.service_id} desconectado del WebSocket service")
    
    async def send_message_to_user(self, user_id: str, message_type: str, data: Dict[str, Any]):
        """Enviar mensaje a un usuario específico"""
        if not self.connection:
            logger.error("No hay conexión al WebSocket service")
            return False
        
        message = {
            "type": "service_message",
            "target_user": user_id,
            "message_type": message_type,
            "data": data,
            "service_id": self.service_id
        }
        
        try:
            await self.connection.send(json.dumps(message))
            logger.info(f"Mensaje enviado a usuario {user_id} desde {self.service_id}")
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a usuario {user_id}: {e}")
            return False
    
    async def send_message_to_room(self, room_id: str, message_type: str, data: Dict[str, Any]):
        """Enviar mensaje a una sala específica"""
        if not self.connection:
            logger.error("No hay conexión al WebSocket service")
            return False
        
        message = {
            "type": "service_room_message",
            "room_id": room_id,
            "message_type": message_type,
            "data": data,
            "service_id": self.service_id
        }
        
        try:
            await self.connection.send(json.dumps(message))
            logger.info(f"Mensaje enviado a sala {room_id} desde {self.service_id}")
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a sala {room_id}: {e}")
            return False
    
    async def send_notification(self, user_id: str, title: str, message: str, notification_type: str = "info"):
        """Enviar notificación a un usuario"""
        notification_data = {
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return await self.send_message_to_user(user_id, "notification", notification_data)
    
    async def send_collaboration_update(self, room_id: str, update_type: str, data: Dict[str, Any]):
        """Enviar actualización de colaboración a una sala"""
        collaboration_data = {
            "update_type": update_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return await self.send_message_to_room(room_id, "collaboration_update", collaboration_data)
    
    async def send_content_update(self, user_id: str, content_id: str, update_type: str, data: Dict[str, Any]):
        """Enviar actualización de contenido a un usuario"""
        content_data = {
            "content_id": content_id,
            "update_type": update_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return await self.send_message_to_user(user_id, "content_update", content_data)
    
    async def send_moderation_result(self, user_id: str, content_id: str, result: str, reason: str = None):
        """Enviar resultado de moderación a un usuario"""
        moderation_data = {
            "content_id": content_id,
            "result": result,  # "approved", "rejected", "pending"
            "reason": reason,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return await self.send_message_to_user(user_id, "moderation_result", moderation_data)

class WebSocketServiceIntegration:
    """Clase para integrar WebSocket en microservicios existentes"""
    
    def __init__(self, service_name: str, websocket_service_url: str = "ws://websocket-service:8000"):
        self.service_name = service_name
        self.websocket_client = WebSocketClient(websocket_service_url)
        self.is_connected = False
    
    async def start(self):
        """Iniciar conexión al WebSocket service"""
        self.is_connected = await self.websocket_client.connect(self.service_name)
        return self.is_connected
    
    async def stop(self):
        """Detener conexión al WebSocket service"""
        await self.websocket_client.disconnect()
        self.is_connected = False
    
    async def notify_user(self, user_id: str, title: str, message: str, notification_type: str = "info"):
        """Enviar notificación a usuario"""
        if self.is_connected:
            return await self.websocket_client.send_notification(user_id, title, message, notification_type)
        return False
    
    async def notify_room(self, room_id: str, message_type: str, data: Dict[str, Any]):
        """Enviar mensaje a sala"""
        if self.is_connected:
            return await self.websocket_client.send_message_to_room(room_id, message_type, data)
        return False
