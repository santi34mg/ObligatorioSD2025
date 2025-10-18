"""
WebSocket Service Base - Comunicación en tiempo real
Este servicio proporciona la infraestructura base para WebSockets
que pueden ser utilizados por otros microservicios
"""

import asyncio
import json
import logging
from typing import Dict, List, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSocket Service", version="1.0.0")

# CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
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
        # Conexiones activas por usuario
        self.active_connections: Dict[str, WebSocket] = {}
        # Salas de chat/colaboración
        self.rooms: Dict[str, Set[str]] = {}
        # Conexiones por sala
        self.room_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Aceptar nueva conexión WebSocket"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"Usuario {user_id} conectado. Total conexiones: {len(self.active_connections)}")
    
    def disconnect(self, user_id: str):
        """Desconectar usuario"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
            # Remover de todas las salas
            for room_id, users in self.rooms.items():
                if user_id in users:
                    users.remove(user_id)
                    # Actualizar conexiones de la sala
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
                    logger.error(f"Error enviando mensaje a sala {room_id}: {e}")
                    # Marcar para desconexión
                    for user_id, ws in self.active_connections.items():
                        if ws == websocket:
                            disconnected_users.append(user_id)
            
            # Limpiar conexiones desconectadas
            for user_id in disconnected_users:
                self.disconnect(user_id)
    
    def join_room(self, user_id: str, room_id: str):
        """Unir usuario a una sala"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
            self.room_connections[room_id] = []
        
        self.rooms[room_id].add(user_id)
        
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            if websocket not in self.room_connections[room_id]:
                self.room_connections[room_id].append(websocket)
        
        logger.info(f"Usuario {user_id} se unió a la sala {room_id}")
    
    def leave_room(self, user_id: str, room_id: str):
        """Remover usuario de una sala"""
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            self.rooms[room_id].remove(user_id)
            
            # Remover WebSocket de la sala
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                if room_id in self.room_connections:
                    self.room_connections[room_id] = [
                        ws for ws in self.room_connections[room_id] if ws != websocket
                    ]
            
            # Si la sala está vacía, eliminarla
            if not self.rooms[room_id]:
                del self.rooms[room_id]
                if room_id in self.room_connections:
                    del self.room_connections[room_id]
            
            logger.info(f"Usuario {user_id} salió de la sala {room_id}")

# Instancia global del gestor de conexiones
manager = ConnectionManager()

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

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Endpoint principal de WebSocket para comunicación en tiempo real"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Procesar mensaje según el tipo
            message_type = message_data.get("type")
            
            if message_type == "join_room":
                room_id = message_data.get("room_id")
                if room_id:
                    manager.join_room(user_id, room_id)
                    # Notificar a otros usuarios de la sala
                    join_message = json.dumps({
                        "type": "user_joined",
                        "user_id": user_id,
                        "room_id": room_id,
                        "message": f"Usuario {user_id} se unió a la sala"
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
                        "message": f"Usuario {user_id} salió de la sala"
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
                # Para actualizaciones de colaboración (documentos, etc.)
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
                # Mensaje genérico - reenviar a la sala si existe
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
    """Obtener información de salas activas"""
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
    """Obtener información de conexiones activas"""
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
