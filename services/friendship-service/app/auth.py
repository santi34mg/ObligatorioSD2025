import uuid
import os
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session

# Must match auth-service SECRET
SECRET = os.getenv("JWT_SECRET", "SECRET")
ALGORITHM = "HS256"

security = HTTPBearer()


# Minimal User model for validation (references same table as auth-service)
class User:
    def __init__(self, id: uuid.UUID, email: str, is_active: bool):
        self.id = id
        self.email = email
        self.is_active = is_active


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Verify JWT token and return current user.
    This validates tokens created by auth-service.
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # fastapi-users includes audience in JWT, so we need to decode with options to ignore it
        payload = jwt.decode(
            token,
            SECRET,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}  # Disable audience verification
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_uuid = uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise credentials_exception
    
    # Verify user exists in database and get user details
    result = await session.execute(
        text("SELECT id, email, is_active FROM auth.\"user\" WHERE id = :user_id"),
        {"user_id": str(user_uuid)}
    )
    user_row = result.first()
    
    if not user_row:
        raise credentials_exception
    
    # Create User object with database data
    return User(
        id=uuid.UUID(str(user_row[0])),
        email=user_row[1],
        is_active=user_row[2]
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
