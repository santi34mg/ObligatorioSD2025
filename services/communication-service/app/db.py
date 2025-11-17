"""
Database utilities for communication service
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
from datetime import datetime
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "umshare")

_client: Optional[AsyncIOMotorClient] = None
_db = None


async def get_db():
    """Get async MongoDB database connection"""
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[MONGO_DB]
        # Create indexes
        await _db["chats"].create_index([("participants", 1)])
        await _db["chats"].create_index([("updated_at", -1)])
        await _db["messages"].create_index([("chat_id", 1), ("created_at", -1)])
        await _db["messages"].create_index([("sender_id", 1)])
    return _db


async def get_user_chats(user_id: str, skip: int = 0, limit: int = 50) -> tuple[List[dict], int]:
    """Get all chats for a user"""
    db = await get_db()
    collection = db["chats"]
    
    # Find chats where user is a participant
    query = {"participants": user_id}
    
    # Get total count
    total = await collection.count_documents(query)
    
    # Get chats sorted by most recent activity
    cursor = collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
    chats = []
    async for chat in cursor:
        chat["id"] = str(chat["_id"])
        chats.append(chat)
    
    return chats, total


async def get_chat_by_id(chat_id: str) -> Optional[dict]:
    """Get a chat by its ID"""
    from bson import ObjectId
    
    if not ObjectId.is_valid(chat_id):
        return None
    
    db = await get_db()
    chat = await db["chats"].find_one({"_id": ObjectId(chat_id)})
    
    if chat:
        chat["id"] = str(chat["_id"])
    
    return chat


async def create_chat(participants: List[str], name: Optional[str] = None) -> str:
    """Create a new chat"""
    db = await get_db()
    
    chat_data = {
        "participants": participants,
        "name": name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_message": None,
        "unread_count": {participant: 0 for participant in participants}
    }
    
    result = await db["chats"].insert_one(chat_data)
    return str(result.inserted_id)


async def get_chat_messages(chat_id: str, skip: int = 0, limit: int = 50) -> tuple[List[dict], int]:
    """Get messages for a chat"""
    from bson import ObjectId
    
    if not ObjectId.is_valid(chat_id):
        return [], 0
    
    db = await get_db()
    collection = db["messages"]
    
    query = {"chat_id": chat_id}
    
    # Get total count
    total = await collection.count_documents(query)
    
    # Get messages sorted by creation time (oldest first)
    cursor = collection.find(query).sort("created_at", 1).skip(skip).limit(limit)
    messages = []
    async for message in cursor:
        message["id"] = str(message["_id"])
        messages.append(message)
    
    return messages, total


async def create_message(chat_id: str, sender_id: str, text: str) -> str:
    """Create a new message in a chat"""
    from bson import ObjectId
    
    db = await get_db()
    
    message_data = {
        "chat_id": chat_id,
        "sender_id": sender_id,
        "text": text,
        "created_at": datetime.utcnow(),
        "read_by": [sender_id]  # Sender has read their own message
    }
    
    result = await db["messages"].insert_one(message_data)
    
    # Update chat's last message and updated_at
    await db["chats"].update_one(
        {"_id": ObjectId(chat_id)},
        {
            "$set": {
                "last_message": text,
                "updated_at": datetime.utcnow()
            },
            "$inc": {
                f"unread_count.{participant}": 1 
                for participant in (await get_chat_by_id(chat_id))["participants"]
                if participant != sender_id
            }
        }
    )
    
    return str(result.inserted_id)


async def mark_messages_as_read(chat_id: str, user_id: str) -> None:
    """Mark all messages in a chat as read by a user"""
    from bson import ObjectId
    
    db = await get_db()
    
    # Add user to read_by array for all messages they haven't read
    await db["messages"].update_many(
        {"chat_id": chat_id, "read_by": {"$ne": user_id}},
        {"$addToSet": {"read_by": user_id}}
    )
    
    # Reset unread count for this user
    await db["chats"].update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": {f"unread_count.{user_id}": 0}}
    )
