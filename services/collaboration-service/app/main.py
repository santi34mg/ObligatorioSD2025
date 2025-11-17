from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from prometheus_fastapi_instrumentator import Instrumentator

from app.db import get_db
from app.schemas import ThreadCreate, ThreadOut, CommentCreate, CommentOut, UserMeta, oid_str
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents

app = FastAPI(title="Collaboration Service", version="1.0.0")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# RabbitMQ global client
rabbitmq_client = None
event_publisher = None

# Get user from headers (until auth-service is ready)
async def current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(default=None, alias="X-User-Name"),
) -> UserMeta:
    return UserMeta(user_id=x_user_id, name=x_user_name)

@app.get("/api/collaboration/health")
async def health():
    return {"status": "ok"}

@app.get("/api/collab/health")
async def health_alias():
    """Health check with short alias"""
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    """Connect to RabbitMQ on startup"""
    global rabbitmq_client, event_publisher
    
    # Connect to RabbitMQ (with error handling)
    try:
        rabbitmq_client = create_rabbitmq_client("collaboration-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        
        # Subscribe to moderation events
        await rabbitmq_client.consume_events(
            [SystemEvents.MODERATION_APPROVED, SystemEvents.MODERATION_REJECTED],
            handle_moderation_event
        )
        print("Collaboration service connected to RabbitMQ")
    except Exception as e:
        print(f"Warning: Could not connect to RabbitMQ: {e}")
        print("Service will continue without async events")
        rabbitmq_client = None
        event_publisher = None


@app.on_event("shutdown")
async def on_shutdown():
    """Disconnect from RabbitMQ"""
    global rabbitmq_client
    
    if rabbitmq_client:
        await rabbitmq_client.disconnect()


async def handle_moderation_event(event_type: str, event_data: dict):
    """Handle moderation events from moderation-service"""
    print(f"Collaboration Service received moderation event: {event_type}")
    print(f"Data: {event_data.get('data', {})}")
    
    # TODO: Update thread/comment status based on moderation results


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
        "status": "published",  # for future moderation
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
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "collaboration.thread_created",
            {
                "thread_id": str(res.inserted_id),
                "title": doc["title"],
                "created_by": user.user_id,
                "tags": doc["tags"],
                "action": "thread_created"
            }
        )
    
    return out

# Listar hilos
@app.get("/api/threads", response_model=List[ThreadOut])
async def list_threads(db=Depends(get_db), q: Optional[str] = None, limit: int = 20, skip: int = 0):
    coll = db["threads"]
    find = {"status": "published"}
    if q:
        # simple search by title (text index)
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

    comment_out = CommentOut(
        id=str(res.inserted_id),
        thread_id=thread_id,
        body=payload.body,
        created_at=doc["created_at"],
        created_by=user,
    )
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "collaboration.comment_created",
            {
                "comment_id": str(res.inserted_id),
                "thread_id": thread_id,
                "created_by": user.user_id,
                "action": "comment_created"
            }
        )
    
    return comment_out

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
