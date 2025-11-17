"""
WebSocket Service Base - Real-time communication
This service provides the base infrastructure for WebSockets
that can be used by other microservices
"""

import asyncio
import json
import logging
from typing import Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSocket Service", version="1.0.0")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# RabbitMQ global client
rabbitmq_client = None
event_publisher = None

# CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos
class WebSocketMessage(BaseModel):
    type: str
    data: dict
    user_id: str = None
    room_id: str = None

class ConnectionManager:
    """Gestor de conexiones WebSocket"""
    
    def __init__(self):
        # Active connections per user
        self.active_connections: Dict[str, WebSocket] = {}
        # Chat/collaboration rooms
        self.rooms: Dict[str, Set[str]] = {}
        # Connections per room
        self.room_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, user_id: str):
        """Disconnect user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
            # Remove from all rooms
            for room_id, users in self.rooms.items():
                if user_id in users:
                    users.remove(user_id)
                    # Update room connections
                    if room_id in self.room_connections:
                        self.room_connections[room_id] = [
                            ws for ws in self.room_connections[room_id] 
                            if ws != self.active_connections.get(user_id)
                        ]
            
            logger.info(f"Usuario {user_id} desconectado. Total conexiones: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Enviar mensaje personal a un usuario específico"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje a {user_id}: {e}")
                self.disconnect(user_id)
    
    async def send_room_message(self, message: str, room_id: str):
        """Enviar mensaje a todos los usuarios de una sala"""
        if room_id in self.room_connections:
            disconnected_users = []
            for websocket in self.room_connections[room_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to room {room_id}: {e}")
                    # Mark for disconnection
                    for user_id, ws in self.active_connections.items():
                        if ws == websocket:
                            disconnected_users.append(user_id)
            
            # Clean disconnected connections
            for user_id in disconnected_users:
                self.disconnect(user_id)
    
    def join_room(self, user_id: str, room_id: str):
        """Join user to a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
            self.room_connections[room_id] = []
        
        self.rooms[room_id].add(user_id)
        
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if websocket not in self.room_connections[room_id]:
                self.room_connections[room_id].append(websocket)
        
        logger.info(f"User {user_id} joined room {room_id}")
    
    def leave_room(self, user_id: str, room_id: str):
        """Remove user from a room"""
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            self.rooms[room_id].remove(user_id)
            
            # Remove WebSocket from room
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                if room_id in self.room_connections:
                    self.room_connections[room_id] = [
                        ws for ws in self.room_connections[room_id] if ws != websocket
                    ]
            
            # If room is empty, delete it
            if not self.rooms[room_id]:
                del self.rooms[room_id]
                if room_id in self.room_connections:
                    del self.room_connections[room_id]
            
            logger.info(f"User {user_id} left room {room_id}")

# Global instance of connection manager
manager = ConnectionManager()

@app.on_event("startup")
async def on_startup():
    """Connect to RabbitMQ on startup and subscribe to all events"""
    global rabbitmq_client, event_publisher
    
    # Connect to RabbitMQ (with error handling)
    try:
        rabbitmq_client = create_rabbitmq_client("websocket-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        
        # Subscribe to ALL events to broadcast them via WebSocket
        await rabbitmq_client.consume_events(
            [
                SystemEvents.USER_REGISTERED,
                SystemEvents.USER_DELETED,
                SystemEvents.CONTENT_CREATED,
                SystemEvents.MODERATION_APPROVED,
                SystemEvents.MODERATION_REJECTED,
                "friendship.request_sent",
                "friendship.accepted",
                "friendship.blocked",
                "collaboration.thread_created",
                "collaboration.comment_created",
                "communication.message_sent"
            ],
            handle_rabbitmq_event
        )
        print("WebSocket service connected to RabbitMQ")
    except Exception as e:
        print(f"Warning: Could not connect to RabbitMQ: {e}")
        print("Service will continue without async events")
        rabbitmq_client = None
        event_publisher = None


@app.on_event("shutdown")
async def on_shutdown():
    """Disconnect from RabbitMQ"""
    global rabbitmq_client
    
    if rabbitmq_client:
        await rabbitmq_client.disconnect()


async def handle_rabbitmq_event(event_type: str, event_data: dict):
    """Handle events from RabbitMQ and broadcast to WebSocket clients"""
    logger.info(f"WebSocket Service received event: {event_type}")
    
    # Broadcast event to all connected clients
    message = json.dumps({
        "type": event_type,
        "data": event_data.get('data', {}),
        "timestamp": event_data.get('timestamp', '')
    })
    
    # Broadcast to all active connections
    for user_id in list(manager.active_connections.keys()):
        await manager.send_personal_message(message, user_id)


@app.get("/")
async def root():
    """Endpoint de salud del servicio"""
    return {
        "service": "WebSocket Service",
        "status": "running",
        "active_connections": len(manager.active_connections),
        "active_rooms": len(manager.rooms)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/ws/health")
async def api_health_check():
    """Health check endpoint with API prefix"""
    return {"status": "healthy"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Main WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message based on type
            message_type = message_data.get("type")
            
            if message_type == "join_room":
                room_id = message_data.get("room_id")
                if room_id:
                    manager.join_room(user_id, room_id)
                    # Notify other users in the room
                    join_message = json.dumps({
                        "type": "user_joined",
                        "user_id": user_id,
                        "room_id": room_id,
                        "message": f"User {user_id} joined the room"
                    })
                    await manager.send_room_message(join_message, room_id)
            
            elif message_type == "leave_room":
                room_id = message_data.get("room_id")
                if room_id:
                    manager.leave_room(user_id, room_id)
                    # Notificar a otros usuarios de la sala
                    leave_message = json.dumps({
                        "type": "user_left",
                        "user_id": user_id,
                        "room_id": room_id,
                        "message": f"User {user_id} left the room"
                    })
                    await manager.send_room_message(leave_message, room_id)
            
            elif message_type == "chat_message":
                room_id = message_data.get("room_id")
                message_text = message_data.get("message")
                if room_id and message_text:
                    # Reenviar mensaje a todos los usuarios de la sala
                    chat_message = json.dumps({
                        "type": "chat_message",
                        "user_id": user_id,
                        "room_id": room_id,
                        "message": message_text,
                        "timestamp": message_data.get("timestamp")
                    })
                    await manager.send_room_message(chat_message, room_id)
            
            elif message_type == "private_message":
                target_user = message_data.get("target_user")
                message_text = message_data.get("message")
                if target_user and message_text:
                    # Enviar mensaje privado
                    private_message = json.dumps({
                        "type": "private_message",
                        "from_user": user_id,
                        "message": message_text,
                        "timestamp": message_data.get("timestamp")
                    })
                    await manager.send_personal_message(private_message, target_user)
            
            elif message_type == "collaboration_update":
                # For collaboration updates (documents, etc.)
                room_id = message_data.get("room_id")
                if room_id:
                    collaboration_message = json.dumps({
                        "type": "collaboration_update",
                        "user_id": user_id,
                        "room_id": room_id,
                        "data": message_data.get("data"),
                        "timestamp": message_data.get("timestamp")
                    })
                    await manager.send_room_message(collaboration_message, room_id)
            
            else:
                # Generic message - forward to room if exists
                room_id = message_data.get("room_id")
                if room_id:
                    await manager.send_room_message(data, room_id)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"Error en WebSocket para usuario {user_id}: {e}")
        manager.disconnect(user_id)

@app.get("/rooms")
async def get_active_rooms():
    """Get information about active rooms"""
    return {
        "rooms": {
            room_id: {
                "user_count": len(users),
                "users": list(users)
            }
            for room_id, users in manager.rooms.items()
        },
        "total_rooms": len(manager.rooms)
    }

@app.get("/connections")
async def get_active_connections():
    """Get information about active connections"""
    return {
        "active_connections": len(manager.active_connections),
        "connected_users": list(manager.active_connections.keys())
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
