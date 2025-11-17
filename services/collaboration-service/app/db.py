import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "umshare")

_client = None
_db = None

async def get_db():
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[MONGO_DB]
        # suggested indexes
        await _db["threads"].create_index([("created_at", -1)])
        await _db["threads"].create_index([("title", "text")])
        await _db["comments"].create_index([("thread_id", 1), ("created_at", 1)])
    return _db
