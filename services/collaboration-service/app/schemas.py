from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# Utilidad para IDs como string
def oid_str(v) -> str:
    return str(v) if v is not None else None

class UserMeta(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None

class ThreadCreate(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    body: str = Field(min_length=1, max_length=20000)
    tags: Optional[List[str]] = None

class ThreadOut(BaseModel):
    id: str
    title: str
    body: str
    tags: List[str] = []
    created_at: datetime
    created_by: Optional[UserMeta] = None
    comments_count: int = 0

class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=10000)

class CommentOut(BaseModel):
    id: str
    thread_id: str
    body: str
    created_at: datetime
    created_by: Optional[UserMeta] = None
