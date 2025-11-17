from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, status
from typing import List, Optional
from prometheus_fastapi_instrumentator import Instrumentator
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents
from datetime import datetime

from app.auth import get_current_user, CurrentUser
from app.db import (
    get_user_chats,
    get_chat_by_id,
    create_chat,
    get_chat_messages,
    create_message,
    mark_messages_as_read
)
from app.schemas import (
    ChatResponse,
    ChatListResponse,
    ChatCreate,
    MessageResponse,
    MessageListResponse,
    MessageCreate
)

app = FastAPI(title="Communication Service")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# RabbitMQ global client
rabbitmq_client = None
event_publisher = None

# Lista de conexiones activas
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


@app.on_event("startup")
async def on_startup():
    """Connect to RabbitMQ on startup"""
    global rabbitmq_client, event_publisher
    
    # Connect to RabbitMQ (with error handling)
    try:
        rabbitmq_client = create_rabbitmq_client("communication-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        print("Communication service connected to RabbitMQ")
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


def chat_to_response(chat: dict, current_user_id: str) -> ChatResponse:
    """Convert MongoDB chat document to ChatResponse"""
    # Get the other participant (for 1-on-1 chats)
    other_participant = None
    for participant in chat.get("participants", []):
        if participant != current_user_id:
            other_participant = participant
            break
    
    # Generate avatar URL
    avatar_name = chat.get("name") or other_participant or "Chat"
    avatar_url = f"https://ui-avatars.com/api/?name={avatar_name}&background=random&size=128"
    
    # Convert ObjectId to integer for frontend
    chat_id = int(str(chat["_id"]), 16) % (10**10)
    
    # Get unread count for current user
    unread_count = chat.get("unread_count", {}).get(current_user_id, 0)
    
    return ChatResponse(
        id=chat_id,
        name=chat.get("name") or other_participant or "Chat",
        avatar=avatar_url,
        lastMessage=chat.get("last_message", ""),
        timestamp=chat.get("updated_at", datetime.utcnow()).isoformat(),
        unread=unread_count,
        online=False,  # TODO: implement online status
        userId=other_participant,
        participantIds=chat.get("participants", [])
    )


def message_to_response(message: dict, current_user_id: str) -> MessageResponse:
    """Convert MongoDB message document to MessageResponse"""
    # Convert ObjectId to integer for frontend
    message_id = int(str(message["_id"]), 16) % (10**10)
    
    return MessageResponse(
        id=message_id,
        chatId=message.get("chat_id", ""),
        senderId=message.get("sender_id", ""),
        text=message.get("text", ""),
        timestamp=message.get("created_at", datetime.utcnow()).isoformat(),
        isMine=message.get("sender_id") == current_user_id,
        createdAt=message.get("created_at", datetime.utcnow()).isoformat()
    )


@app.get("/api/communication/chats", response_model=List[ChatResponse])
async def list_chats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get all chats for the current user"""
    chats, total = await get_user_chats(current_user.id, skip=skip, limit=limit)
    
    chat_responses = [chat_to_response(chat, current_user.id) for chat in chats]
    
    return chat_responses


@app.post("/api/communication/chats", response_model=ChatResponse)
async def create_new_chat(
    chat_data: ChatCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create a new chat"""
    # Add current user to participants if not already included
    participants = list(set(chat_data.participant_ids + [current_user.id]))
    
    # Create the chat
    chat_id = await create_chat(participants, chat_data.name)
    
    # Get the created chat
    chat = await get_chat_by_id(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat"
        )
    
    return chat_to_response(chat, current_user.id)


@app.get("/api/communication/chats/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get a specific chat by ID"""
    chat = await get_chat_by_id(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Verify user is a participant
    if current_user.id not in chat.get("participants", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat"
        )
    
    return chat_to_response(chat, current_user.id)


@app.get("/api/communication/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def list_messages(
    chat_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get messages for a chat"""
    # Verify user has access to the chat
    chat = await get_chat_by_id(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if current_user.id not in chat.get("participants", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat"
        )
    
    messages, total = await get_chat_messages(chat_id, skip=skip, limit=limit)
    
    message_responses = [message_to_response(msg, current_user.id) for msg in messages]
    
    return message_responses


@app.post("/api/communication/chats/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Send a message to a chat"""
    # Verify user has access to the chat
    chat = await get_chat_by_id(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if current_user.id not in chat.get("participants", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat"
        )
    
    # Create the message
    message_id = await create_message(chat_id, current_user.id, message_data.text)
    
    # Get the created message
    from app.db import get_db
    from bson import ObjectId
    
    db = await get_db()
    message = await db["messages"].find_one({"_id": ObjectId(message_id)})
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create message"
        )
    
    message["id"] = str(message["_id"])
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "communication.message_sent",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "sender_id": current_user.id,
                "text": message_data.text
            }
        )
    
    return message_to_response(message, current_user.id)


@app.post("/api/communication/chats/{chat_id}/read")
async def mark_as_read(
    chat_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Mark all messages in a chat as read"""
    # Verify user has access to the chat
    chat = await get_chat_by_id(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if current_user.id not in chat.get("participants", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this chat"
        )
    
    await mark_messages_as_read(chat_id, current_user.id)
    
    return {"status": "ok", "message": "Messages marked as read"}


@app.websocket("/api/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    #Canal de chat en tiempo real
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Nuevo mensaje: {data}")
            
            # Publish message event
            global event_publisher
            if event_publisher:
                await event_publisher.publish_event(
                    "communication.message_sent",
                    {
                        "message": data,
                        "action": "message_broadcasted"
                    }
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/communication/health")
def root():
    return {"status": "ok"}
