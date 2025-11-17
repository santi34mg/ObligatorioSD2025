import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_fastapi_instrumentator import Instrumentator

from app.db import get_async_session, create_db_and_tables
from app.models import Friendship
from app.schemas import (
    FriendshipRequest,
    FriendshipResponse,
    FriendsList,
    FriendWithDetails,
)
from app.auth import get_current_active_user, User
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents

app = FastAPI(title="Friendship Service")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# RabbitMQ global client
rabbitmq_client = None
event_publisher = None

@app.on_event("startup")
async def on_startup():
    """Create database tables on startup and connect to RabbitMQ"""
    global rabbitmq_client, event_publisher
    
    await create_db_and_tables()
    
    # Connect to RabbitMQ (with error handling)
    try:
        rabbitmq_client = create_rabbitmq_client("friendship-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        
        # Subscribe to user events
        await rabbitmq_client.consume_events(
            [SystemEvents.USER_REGISTERED, SystemEvents.USER_DELETED],
            handle_user_event
        )
        print("Friendship service connected to RabbitMQ")
    except Exception as e:
        print(f"Warning: Could not connect to RabbitMQ: {e}")
        print("Service will continue without async events")
        rabbitmq_client = None
        event_publisher = None


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
        text("SELECT id FROM auth.\"user\" WHERE id = :friend_id"),
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
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "friendship.request_sent",
            {
                "user_id": str(current_user.id),
                "friend_id": str(request.friend_id),
                "friendship_id": str(new_friendship.id),
                "action": "friend_request_sent"
            }
        )
    
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
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "friendship.accepted",
            {
                "user_id": str(friendship.user_id),
                "friend_id": str(friendship.friend_id),
                "friendship_id": str(friendship.id),
                "accepted_by": str(current_user.id),
                "action": "friend_request_accepted"
            }
        )
    
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
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "friendship.blocked",
            {
                "user_id": str(friendship.user_id),
                "friend_id": str(friendship.friend_id),
                "friendship_id": str(friendship.id),
                "blocked_by": str(current_user.id),
                "action": "user_blocked"
            }
        )
    
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
    Remove a friendship (either accepted or pending).
    """
    # Find friendship in either direction
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
    
    await session.delete(friendship)
    await session.commit()
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "friendship.removed",
            {
                "user_id": str(current_user.id),
                "friend_id": str(friend_id),
                "action": "friendship_removed"
            }
        )


@app.on_event("shutdown")
async def on_shutdown():
    """Disconnect from RabbitMQ"""
    global rabbitmq_client
    
    if rabbitmq_client:
        await rabbitmq_client.disconnect()


async def handle_user_event(event_type: str, event_data: dict):
    """Handle user events from auth-service"""
    print(f"Friendship Service received user event: {event_type}")
    print(f"Data: {event_data.get('data', {})}")
    
    # TODO: Implement business logic based on user events
    # For example, if a user is deleted, remove all their friendships

