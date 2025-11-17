from fastapi import UploadFile, File, Form, Depends, HTTPException, Query, status, FastAPI
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
import os
from prometheus_fastapi_instrumentator import Instrumentator

from app.storage import upload_to_minio
from app.db import (
    get_db,
    insert_metadata,
    get_materials,
    get_material_by_id,
    extract_file_format
)
from app.schemas import (
    MaterialResponse,
    MaterialListResponse,
    PostResponse,
    PostListResponse,
    PostUser
)
from typing import Literal
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents

MaterialType = Literal[
    "Parcial de semestre anterior",
    "Examen de semestre anterior",
    "Apuntes",
    "Práctico"
]
from app.auth import get_current_user_optional, get_current_user, CurrentUser

app = FastAPI(title="Content Service", version="1.0.0")

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# RabbitMQ global client
rabbitmq_client = None
event_publisher = None


@app.get("/api/content/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "content-service"}


@app.on_event("startup")
async def on_startup():
    """Initialize services on startup"""
    global rabbitmq_client, event_publisher
    
    # Initialize MinIO bucket with public read policy
    try:
        from app.init_minio import init_minio
        init_minio()
    except Exception as e:
        print(f"Warning: MinIO initialization failed: {e}")
    
    # Connect to RabbitMQ (with error handling)
    try:
        rabbitmq_client = create_rabbitmq_client("content-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        
        # Subscribe to moderation events
        await rabbitmq_client.consume_events(
            [SystemEvents.MODERATION_APPROVED, SystemEvents.MODERATION_REJECTED],
            handle_moderation_event
        )
        print("Content service connected to RabbitMQ")
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
    print(f"Content Service received moderation event: {event_type}")
    print(f"Data: {event_data.get('data', {})}")
    
    # TODO: Update material approval status based on moderation results
    # For example, auto-approve materials that passed moderation


def get_user_name_from_email(email: Optional[str]) -> str:
    """Extraer el nombre de la email (temporalmente hasta que tengamos el nombre de usuario en JWT o llamemos al servicio de usuarios)"""
    if email:
        return email.split("@")[0]
    return "Anonymous"


def get_user_avatar(email: Optional[str]) -> str:
    """Generar la URL del avatar desde la email"""
    if email:
        return f"https://ui-avatars.com/api/?name={email.split('@')[0]}&background=random&size=128"
    return "https://ui-avatars.com/api/?name=Anonymous&background=random&size=128"


def material_to_post(material: dict, user_email: Optional[str] = None) -> PostResponse:
    """Convertir el material de MongoDB al formato Post esperado por el frontend"""
    uploader = material.get("uploader") or user_email or "anonymous@example.com"
    
    user_name = get_user_name_from_email(uploader)
    user_avatar = get_user_avatar(uploader)
    
    content_type = material.get("content_type", "")
    file_url = material.get("url", "")
    
    # Determine if it's an image
    is_image = content_type.startswith("image/")
    
    return PostResponse(
        id=int(material.get("id", "").replace("-", ""), 16) % (10**10),  # Convert ObjectId to number
        user=PostUser(
            name=user_name,
            avatar=user_avatar
        ),
        date=material.get("fecha_subida", datetime.utcnow()),
        title=material.get("title", ""),
        content=material.get("description", ""),
        commentCount=0,  # TODO: implement comments later
        likes=0,  # TODO: implement likes later
        image=file_url if is_image else None,
        fileUrl=file_url if not is_image else None,
        fileName=material.get("filename", ""),
        fileType=content_type
    )


@app.get("/api/content/posts", response_model=PostListResponse)
async def list_posts_api(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    List posts/materials in API format (with pagination).
    """
    materials, total = await get_materials(
        skip=skip,
        limit=limit,
        aprobado=True  # Only show approved materials
    )
    
    print(f"DEBUG: Found {total} materials, got {len(materials)} materials")
    print(f"DEBUG: Materials: {materials}")
    
    posts = [material_to_post(m) for m in materials]
    
    print(f"DEBUG: Converted to {len(posts)} posts")
    
    return PostListResponse(posts=posts, total=total)


@app.get("/api/content/documents", response_model=MaterialListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    aprobado: Optional[bool] = Query(None, description="Filter by approved status"),
    id_asignatura: Optional[str] = Query(None, description="Filter by course/subject"),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    Listar materiales en el formato API (para el health check y el uso del administrador).
    Los usuarios no autenticados solo ven materiales aprobados.
    """
    skip = (page - 1) * page_size
    
    # Non-authenticated users can only see approved materials
    if current_user is None:
        aprobado = True
    
    materials, total = await get_materials(
        skip=skip,
        limit=page_size,
        aprobado=aprobado,
        id_asignatura=id_asignatura
    )
    
    material_responses = [
        MaterialResponse(
            id=m["id"],
            title=m.get("title", ""),
            description=m.get("description", ""),
            url=m.get("url", ""),
            filename=m.get("filename", ""),
            uploader=m.get("uploader", "anonymous"),
            fecha_subida=m.get("fecha_subida", datetime.utcnow()),
            tipo=m.get("tipo"),
            formato=m.get("formato"),
            size=m.get("size"),
            aprobado=m.get("aprobado", False),
            content_type=m.get("content_type", "application/octet-stream")
        )
        for m in materials
    ]
    
    return MaterialListResponse(
        materials=material_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@app.get("/api/content/materials/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: str,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """Get a specific material by its ID"""
    material = await get_material_by_id(material_id)
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Non-authenticated users can only see approved materials
    # TODO: Allow users to see their own materials even if not approved
    if current_user is None and not material.get("aprobado", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Material not available"
        )
    
    return MaterialResponse(
        id=material["id"],
        title=material.get("title", ""),
        description=material.get("description", ""),
        url=material.get("url", ""),
        filename=material.get("filename", ""),
        uploader=material.get("uploader", "anonymous"),
        fecha_subida=material.get("fecha_subida", datetime.utcnow()),
        tipo=material.get("tipo"),
        formato=material.get("formato"),
        size=material.get("size"),
        aprobado=material.get("aprobado", False),
        content_type=material.get("content_type", "application/octet-stream")
    )


@app.post("/api/content/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    tipo: Optional[MaterialType] = Form(None),
    id_asignatura: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Upload a file to MinIO and save metadata in MongoDB.
    Requires authentication (API version).
    """
    # Read file content once
    content = await file.read()
    file_size = len(content)
    
    # Upload file to MinIO (pass content to avoid reading twice)
    file_url, _ = await upload_to_minio(file, content)
    
    # Extract file format
    formato = extract_file_format(file.content_type or "", file.filename or "")
    
    # Prepare metadata
    metadata = {
        "filename": file.filename or "unknown",
        "title": title,
        "description": description,
        "uploader": current_user.email or str(current_user.id),
        "url": file_url,
        "content_type": file.content_type or "application/octet-stream",
        "fecha_subida": datetime.utcnow(),
        "tipo": tipo,
        "formato": formato,
        "size": file_size,
        "aprobado": True,  # Auto-approve materials (moderation disabled for now)
        "id_asignatura": id_asignatura,
        "id_usuario": str(current_user.id)
    }
    
    # Save to MongoDB
    material_id = await insert_metadata(metadata)
    
    # Publish event
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "content.created",
            {
                "material_id": material_id,
                "title": title,
                "uploader": current_user.email,
                "user_id": str(current_user.id),
                "tipo": tipo,
                "action": "content_uploaded"
            }
        )
    
    return {
        "message": "Documento subido exitosamente",
        "id": material_id,
        "url": file_url,
        "title": title,
        "aprobado": True
    }
