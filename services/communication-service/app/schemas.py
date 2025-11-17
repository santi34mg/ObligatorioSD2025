"""
Pydantic schemas for communication service
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatBase(BaseModel):
    """Base chat model"""
    name: Optional[str] = None
    participants: List[str]


class ChatCreate(BaseModel):
    """Schema for creating a chat"""
    participant_ids: List[str] = Field(..., alias="participantIds")
    name: Optional[str] = None
    
    class Config:
        populate_by_name = True


class ChatResponse(BaseModel):
    """Chat response model matching frontend expectations"""
    id: int  # Frontend expects number
    name: str
    avatar: str
    lastMessage: str = ""
    timestamp: str
    unread: int = 0
    online: bool = False
    userId: Optional[str] = None
    participantIds: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True


class MessageBase(BaseModel):
    """Base message model"""
    text: str


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    chat_id: int = Field(..., alias="chatId")
    text: str
    
    class Config:
        populate_by_name = True


class MessageResponse(BaseModel):
    """Message response model matching frontend expectations"""
    id: int  # Frontend expects number
    chatId: int
    senderId: str
    text: str
    timestamp: str
    isMine: bool
    createdAt: Optional[str] = None
    
    class Config:
        populate_by_name = True


class ChatListResponse(BaseModel):
    """Response for list of chats"""
    chats: List[ChatResponse] = []
    total: int = 0


class MessageListResponse(BaseModel):
    """Response for list of messages"""
    messages: List[MessageResponse] = []
    total: int = 0
