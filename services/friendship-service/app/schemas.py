import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FriendshipRequest(BaseModel):
    """Schema for creating a friend request"""
    friend_id: uuid.UUID = Field(..., description="UUID of the user to send friend request to")


class FriendshipResponse(BaseModel):
    """Schema for friendship response"""
    id: uuid.UUID
    user_id: uuid.UUID
    friend_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FriendWithDetails(BaseModel):
    """Schema for friend with user details"""
    friendship_id: uuid.UUID
    friend_user_id: uuid.UUID
    friend_email: str
    status: str
    created_at: datetime
    updated_at: datetime


class FriendsList(BaseModel):
    """Schema for list of friends"""
    friends: list[FriendWithDetails]
    total: int


class FriendshipUpdate(BaseModel):
    """Schema for updating friendship status"""
    status: str = Field(..., description="New status: accepted, blocked")
