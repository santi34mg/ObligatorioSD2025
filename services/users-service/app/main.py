import uuid
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_fastapi_instrumentator import Instrumentator

from app.db import get_async_session
from app.models import User
from app.schemas import UserPublicInfo, UserDetailInfo, UserListResponse, UserUpdate
from app.auth import get_current_active_user

app = FastAPI(title="Users Service", version="1.0.0")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/api/users/health")
def root():
    return {"message": "Users Service is online"}


@app.get("/api/users/list", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    email_filter: Optional[str] = Query(None, description="Filter by email substring"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all users with pagination and optional filters.
    Requires authentication.
    """
    # Build base query
    stmt = select(User)
    count_stmt = select(func.count(User.id))
    
    # Apply filters
    if email_filter:
        stmt = stmt.where(User.email.ilike(f"%{email_filter}%"))
        count_stmt = count_stmt.where(User.email.ilike(f"%{email_filter}%"))
    
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
        count_stmt = count_stmt.where(User.is_active == is_active)
    
    if is_verified is not None:
        stmt = stmt.where(User.is_verified == is_verified)
        count_stmt = count_stmt.where(User.is_verified == is_verified)
    
    # Get total count
    count_result = await session.execute(count_stmt)
    total = count_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    
    # Order by email for consistent results
    stmt = stmt.order_by(User.email)
    
    # Execute query
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    # Convert to public info (excludes sensitive fields)
    users_public = [UserPublicInfo.model_validate(user) for user in users]
    
    return UserListResponse(
        users=users_public,
        total=total,
        page=page,
        page_size=page_size
    )


@app.get("/api/users/public/{user_id}", response_model=UserPublicInfo)
async def get_user_public(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get public information about a specific user.
    Does not require authentication (for displaying user info in posts).
    """
    # Query user by UUID
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Return public info only
    return UserPublicInfo.model_validate(user)


@app.get("/api/users/{user_id}", response_model=UserDetailInfo)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get detailed information about a specific user.
    Requires authentication.
    """
    # Query user by UUID
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Return detailed info
    return UserDetailInfo.model_validate(user)


@app.post("/api/users/{user_id}", response_model=UserDetailInfo)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update user information.
    
    Authorization rules:
    - Users can update their own is_verified status
    - Only superusers can update other users' fields
    - Only superusers can modify is_superuser field
    - Cannot modify email or password (handled by auth-service)
    
    Requires authentication.
    """
    # Query the target user
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    target_user = result.scalar_one_or_none()
    
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Authorization checks
    is_self_update = current_user.id == user_id
    is_admin = current_user.is_superuser
    
    # Check if trying to update someone else without admin privileges
    if not is_self_update and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update other users"
        )
    
    # Check if trying to update is_superuser without admin privileges
    if user_update.is_superuser is not None and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can modify is_superuser field"
        )
    
    # Apply updates
    updated = False
    
    if user_update.is_active is not None:
        target_user.is_active = user_update.is_active
        updated = True
    
    if user_update.is_verified is not None:
        target_user.is_verified = user_update.is_verified
        updated = True
    
    if user_update.is_superuser is not None:
        target_user.is_superuser = user_update.is_superuser
        updated = True
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Commit changes
    await session.commit()
    await session.refresh(target_user)
    
    return UserDetailInfo.model_validate(target_user)
