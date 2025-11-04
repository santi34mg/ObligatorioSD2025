import uuid
from typing import List
from pydantic import BaseModel, Field


class UserPublicInfo(BaseModel):
    """Public user information (safe to expose to all authenticated users)"""
    id: uuid.UUID
    email: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserDetailInfo(UserPublicInfo):
    """Detailed user information (includes sensitive fields like is_superuser)"""
    is_superuser: bool

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response schema for listing users with pagination info"""
    users: List[UserPublicInfo]
    total: int
    page: int
    page_size: int


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    is_active: bool | None = Field(None, description="Update active status")
    is_verified: bool | None = Field(None, description="Update verified status")
    is_superuser: bool | None = Field(None, description="Update superuser status (admin only)")
