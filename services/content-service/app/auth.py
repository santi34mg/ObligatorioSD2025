import uuid
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# Must match auth-service SECRET
SECRET = os.getenv("JWT_SECRET", "SECRET")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Simple user model for content service"""
    def __init__(self, id: uuid.UUID, email: Optional[str] = None):
        self.id = id
        self.email = email


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[CurrentUser]:
    """
    Optional authentication - returns user if token is valid, None otherwise.
    Used for endpoints that work with or without authentication.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
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
            return None
        user_uuid = uuid.UUID(user_id)
        # Try to get email from JWT payload
        email = payload.get("email") or payload.get("username")
        return CurrentUser(id=user_uuid, email=email)
    except (JWTError, ValueError):
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> CurrentUser:
    """
    Required authentication - returns user if token is valid, raises exception otherwise.
    """
    user = await get_current_user_optional(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

