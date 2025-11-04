from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.db import get_db
from app.schemas import ThreadCreate, ThreadOut, CommentCreate, CommentOut, UserMeta, oid_str

app = FastAPI(title="Collaboration Service", version="1.0.0")

# Tomamos usuario de headers (hasta que esté el auth-service)
async def current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(default=None, alias="X-User-Name"),
) -> UserMeta:
    return UserMeta(user_id=x_user_id, name=x_user_name)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Crear hilo
@app.post("/api/threads", response_model=ThreadOut)
async def create_thread(payload: ThreadCreate, db=Depends(get_db), user: UserMeta = Depends(current_user)):
    doc = {
        "title": payload.title,
        "body": payload.body,
        "tags": payload.tags or [],
        "created_at": datetime.utcnow(),
        "created_by": user.model_dump(),
        "comments_count": 0,
        "status": "published",  # para moderación futura
    }
    res = await db["threads"].insert_one(doc)
    out = ThreadOut(
        id=str(res.inserted_id),
        title=doc["title"],
        body=doc["body"],
        tags=doc["tags"],
        created_at=doc["created_at"],
        created_by=user,
        comments_count=0,
    )
    return out

# Listar hilos
@app.get("/api/threads", response_model=List[ThreadOut])
async def list_threads(db=Depends(get_db), q: Optional[str] = None, limit: int = 20, skip: int = 0):
    coll = db["threads"]
    find = {"status": "published"}
    if q:
        # búsqueda simple por título (índice text)
        find = {"$and": [find, {"$text": {"$search": q}}]}
    cursor = coll.find(find).sort("created_at", -1).skip(skip).limit(min(limit, 100))
    items = []
    async for t in cursor:
        items.append(
            ThreadOut(
                id=oid_str(t.get("_id")),
                title=t["title"],
                body=t["body"],
                tags=t.get("tags", []),
                created_at=t["created_at"],
                created_by=t.get("created_by"),
                comments_count=t.get("comments_count", 0),
            )
        )
    return items

# Obtener un hilo
@app.get("/api/threads/{thread_id}", response_model=ThreadOut)
async def get_thread(thread_id: str, db=Depends(get_db)):
    t = await db["threads"].find_one({"_id": ObjectId(thread_id)})
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return ThreadOut(
        id=oid_str(t["_id"]),
        title=t["title"],
        body=t["body"],
        tags=t.get("tags", []),
        created_at=t["created_at"],
        created_by=t.get("created_by"),
        comments_count=t.get("comments_count", 0),
    )

# Comentar un hilo
@app.post("/api/threads/{thread_id}/comments", response_model=CommentOut)
async def add_comment(thread_id: str, payload: CommentCreate, db=Depends(get_db), user: UserMeta = Depends(current_user)):
    if not ObjectId.is_valid(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread id")
    thread = await db["threads"].find_one({"_id": ObjectId(thread_id)})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    doc = {
        "thread_id": ObjectId(thread_id),
        "body": payload.body,
        "created_at": datetime.utcnow(),
        "created_by": user.model_dump(),
    }
    res = await db["comments"].insert_one(doc)
    # aumentar contador
    await db["threads"].update_one({"_id": ObjectId(thread_id)}, {"$inc": {"comments_count": 1}})

    return CommentOut(
        id=str(res.inserted_id),
        thread_id=thread_id,
        body=payload.body,
        created_at=doc["created_at"],
        created_by=user,
    )

# Listar comentarios de un hilo
@app.get("/api/threads/{thread_id}/comments", response_model=List[CommentOut])
async def list_comments(thread_id: str, db=Depends(get_db), limit: int = 50, skip: int = 0):
    if not ObjectId.is_valid(thread_id):
        raise HTTPException(status_code=400, detail="Invalid thread id")
    cursor = db["comments"].find({"thread_id": ObjectId(thread_id)}).sort("created_at", 1).skip(skip).limit(min(limit, 200))
    items = []
    async for c in cursor:
        items.append(
            CommentOut(
                id=oid_str(c["_id"]),
                thread_id=thread_id,
                body=c["body"],
                created_at=c["created_at"],
                created_by=c.get("created_by"),
            )
        )
    return items
