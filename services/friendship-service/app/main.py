import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session, create_db_and_tables
from app.models import Friendship
from app.schemas import (
    FriendshipRequest,
    FriendshipResponse,
    FriendsList,
    FriendWithDetails,
)
from app.auth import get_current_active_user, User

app = FastAPI(title="Friendship Service")


@app.on_event("startup")
async def on_startup():
    """Create database tables on startup"""
    await create_db_and_tables()


@app.get("/api/friendships/health")
def root():
    return {"message": "Friendship Service is online"}


@app.post("/friendships/request", response_model=FriendshipResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    request: FriendshipRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Send a friend request to another user.
    Creates a friendship with status='pending'.
    """
    # Validate not sending to self
    if current_user.id == request.friend_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself"
        )
    
    # Check if user exists
    result = await session.execute(
        text("SELECT id FROM \"user\" WHERE id = :friend_id"),
        {"friend_id": str(request.friend_id)}
    )
    if not result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if friendship already exists (in either direction)
    stmt = select(Friendship).where(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == request.friend_id),
            and_(Friendship.user_id == request.friend_id, Friendship.friend_id == current_user.id),
        )
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Friendship already exists with status: {existing.status}"
        )
    
    # Create new friendship
    new_friendship = Friendship(
        user_id=current_user.id,
        friend_id=request.friend_id,
        status="pending",
    )
    
    session.add(new_friendship)
    await session.commit()
    await session.refresh(new_friendship)
    
    return new_friendship


@app.post("/friendships/{friendship_id}/accept", response_model=FriendshipResponse)
async def accept_friend_request(
    friendship_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Accept a pending friend request.
    Only the recipient (friend_id) can accept the request.
    """
    # Get the friendship
    stmt = select(Friendship).where(Friendship.id == friendship_id)
    result = await session.execute(stmt)
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    # Verify current user is the recipient (friend_id)
    if friendship.friend_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recipient can accept the friend request"
        )
    
    # Verify status is pending
    if friendship.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept friendship with status: {friendship.status}"
        )
    
    # Update status
    friendship.status = "accepted"
    friendship.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(friendship)
    
    return friendship


@app.post("/friendships/{friendship_id}/block", response_model=FriendshipResponse)
async def block_user(
    friendship_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Block a user. Can be done on any friendship where user is involved.
    """
    # Get the friendship
    stmt = select(Friendship).where(Friendship.id == friendship_id)
    result = await session.execute(stmt)
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    # Verify current user is involved in this friendship
    if friendship.user_id != current_user.id and friendship.friend_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this friendship"
        )
    
    # Update status
    friendship.status = "blocked"
    friendship.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(friendship)
    
    return friendship


@app.get("/friendships/", response_model=FriendsList)
async def list_friends(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, accepted, blocked"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all friendships for the current user.
    Returns friends with their details.
    """
    # Build query - get friendships where user is either user_id or friend_id
    stmt = select(Friendship).where(
        or_(
            Friendship.user_id == current_user.id,
            Friendship.friend_id == current_user.id,
        )
    )
    
    # Apply status filter if provided
    if status_filter:
        stmt = stmt.where(Friendship.status == status_filter)
    
    result = await session.execute(stmt)
    friendships = result.scalars().all()
    
    # Get friend details
    friends_with_details = []
    for friendship in friendships:
        # Determine which user is the friend
        friend_user_id = friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id
        
        # Get friend email from user table
        user_result = await session.execute(
            text("SELECT email FROM \"user\" WHERE id = :user_id"),
            {"user_id": str(friend_user_id)}
        )
        user_row = user_result.first()
        friend_email = user_row[0] if user_row else "unknown@example.com"
        
        friends_with_details.append(
            FriendWithDetails(
                friendship_id=friendship.id,
                friend_user_id=friend_user_id,
                friend_email=friend_email,
                status=friendship.status,
                created_at=friendship.created_at,
                updated_at=friendship.updated_at,
            )
        )
    
    return FriendsList(friends=friends_with_details, total=len(friends_with_details))


@app.delete("/friendships/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    friend_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Remove a friendship / unfriend / cancel friend request.
    Deletes the friendship record.
    """
    # Find the friendship (in either direction)
    stmt = select(Friendship).where(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
            and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id),
        )
    )
    result = await session.execute(stmt)
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    # Delete the friendship
    await session.delete(friendship)
    await session.commit()
    
    return None
