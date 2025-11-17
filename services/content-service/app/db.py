from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

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
        await _db["materials"].create_index([("fecha_subida", -1)])
        await _db["materials"].create_index([("title", "text"), ("description", "text")])
        await _db["materials"].create_index([("aprobado", 1)])
        await _db["materials"].create_index([("id_usuario", 1)])
        await _db["materials"].create_index([("id_asignatura", 1)])
    return _db


def get_collection():
    """Get sync MongoDB collection (for backward compatibility)"""
    client = MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    return db["materials"]


async def insert_metadata(data: dict):
    """Insert material metadata into MongoDB"""
    db = await get_db()
    # Add fecha_subida if not present
    if "fecha_subida" not in data:
        data["fecha_subida"] = datetime.utcnow()
    # Auto-approve materials by default (can be changed for moderation workflow)
    if "aprobado" not in data:
        data["aprobado"] = True
    result = await db["materials"].insert_one(data)
    return str(result.inserted_id)


async def get_materials(
    skip: int = 0,
    limit: int = 20,
    aprobado: Optional[bool] = None,
    id_usuario: Optional[str] = None,
    id_asignatura: Optional[str] = None
) -> tuple[List[dict], int]:
    """Get materials with optional filters"""
    db = await get_db()
    collection = db["materials"]
    
    # Build query
    query = {}
    if aprobado is not None:
        query["aprobado"] = aprobado
    if id_usuario is not None:
        query["id_usuario"] = id_usuario
    if id_asignatura is not None:
        query["id_asignatura"] = id_asignatura
    
    # Get total count
    total = await collection.count_documents(query)
    
    # Get materials
    cursor = collection.find(query).sort("fecha_subida", -1).skip(skip).limit(limit)
    materials = []
    async for material in cursor:
        material["id"] = str(material["_id"])
        materials.append(material)
    
    return materials, total


async def get_material_by_id(material_id: str) -> Optional[dict]:
    """Get a single material by ID"""
    if not ObjectId.is_valid(material_id):
        return None
    
    db = await get_db()
    material = await db["materials"].find_one({"_id": ObjectId(material_id)})
    
    if material:
        material["id"] = str(material["_id"])
    
    return material


def extract_file_format(content_type: str, filename: str) -> Optional[str]:
    """Extract file format from content_type or filename"""
    # Map content types to formats
    content_type_map = {
        "application/pdf": "pdf",
        "image/jpeg": "jpg",
        "image/png": "png",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/plain": "txt",
        "text/x-python": "py",
        "text/x-java-source": "java",
        "audio/mpeg": "mp3",
        "video/mp4": "mp4",
    }
    
    # Try content type first
    if content_type in content_type_map:
        return content_type_map[content_type]
    
    # Try filename extension
    if filename:
        ext = filename.split(".")[-1].lower()
        if ext in ["pdf", "jpg", "png", "docx", "pptx", "xlsx", "py", "java", "mp3", "mp4", "txt"]:
            return ext
    
    return None
