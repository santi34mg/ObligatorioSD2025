from fastapi import UploadFile, File, Form, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
import os

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

MaterialType = Literal[
    "Parcial de semestre anterior",
    "Examen de semestre anterior",
    "Apuntes",
    "Práctico"
]
from app.auth import get_current_user_optional, get_current_user, CurrentUser

from fastapi import FastAPI

app = FastAPI(title="Content Service", version="1.0.0")


@app.get("/api/content/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "content-service"}


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
    uploader_email = material.get("uploader") or user_email or "anonymous@example.com"
    
    return PostResponse(
        id=int(material.get("id", "").replace("-", ""), 16) % (10**10),  # Convert ObjectId to number
        user=PostUser(
            name=get_user_name_from_email(uploader_email),
            avatar=get_user_avatar(uploader_email)
        ),
        date=material.get("fecha_subida", datetime.utcnow()),
        content=f"{material.get('title', '')}\n{material.get('description', '')}".strip(),
        commentCount=0,  # TODO: implement comments later
        likes=0,  # TODO: implement likes later
        image=material.get("url") if material.get("content_type", "").startswith("image/") else None
    )


@app.get("/api/content/posts", response_model=PostListResponse)
async def list_posts_api(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    Listar posts/materiales en formato API (con paginación).
    """
    materials, total = await get_materials(
        skip=skip,
        limit=limit,
        aprobado=True  # Only show approved materials
    )
    
    posts = [material_to_post(m) for m in materials]
    
    return PostListResponse(posts=posts, total=total)


@app.get("/content/posts")
async def list_posts(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    Listar posts/materiales en formato que espera el frontend.
    Devuelve un array directamente (sin wrapper).
    Los usuarios no autenticados solo ven materiales aprobados.
    Los usuarios autenticados ven materiales aprobados + sus propios materiales no publicados.
    """
    # Por ahora, mostrar solo materiales aprobados a todos
    # TODO: Mostrar los materiales propios incluso si no están aprobados
    materials, total = await get_materials(
        skip=skip,
        limit=limit,
        aprobado=True  # Only show approved materials
    )
    
    posts = [material_to_post(m) for m in materials]
    
    # Frontend espera un array directamente, no un objeto
    return posts


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
            tamaño=m.get("tamaño"),
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
    """Obtener un material específico por su ID"""
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
        tamaño=material.get("tamaño"),
        aprobado=material.get("aprobado", False),
        content_type=material.get("content_type", "application/octet-stream")
    )


@app.post("/content/upload")
async def upload_file_frontend(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    tipo: Optional[MaterialType] = Form(None),
    id_asignatura: Optional[str] = Form(None),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    Subir un archivo a MinIO y guardar la metadata en MongoDB.
    Versión compatible con el frontend (autenticación opcional).
    """
    # Read file content once
    content = await file.read()
    file_size = len(content)
    
    # Upload file to MinIO (pass content to avoid reading twice)
    file_url, _ = await upload_to_minio(file, content)
    
    # Extract file format
    formato = extract_file_format(file.content_type or "", file.filename or "")
    
    # Use authenticated user if available, otherwise anonymous
    uploader_email = current_user.email if current_user else "anonymous"
    user_id = str(current_user.id) if current_user else None
    
    # Prepare metadata
    metadata = {
        "filename": file.filename or "unknown",
        "title": title,
        "description": description,
        "uploader": uploader_email,
        "url": file_url,
        "content_type": file.content_type or "application/octet-stream",
        "fecha_subida": datetime.utcnow(),
        "tipo": tipo,
        "formato": formato,
        "tamaño": file_size,
        "aprobado": False,  # Materials need to be reviewed first
        "id_asignatura": id_asignatura,
        "id_usuario": user_id
    }
    
    # Save to MongoDB
    material_id = await insert_metadata(metadata)
    
    return {
        "message": "Documento subido exitosamente",
        "id": material_id,
        "url": file_url,
        "title": title,
        "aprobado": False
    }


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
    Subir un archivo a MinIO y guardar la metadata en MongoDB.
    Requiere autenticación (versión API).
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
        "tamaño": file_size,
        "aprobado": False,  # Materials need to be reviewed first
        "id_asignatura": id_asignatura,
        "id_usuario": str(current_user.id)
    }
    
    # Save to MongoDB
    material_id = await insert_metadata(metadata)
    
    return {
        "message": "Documento subido exitosamente",
        "id": material_id,
        "url": file_url,
        "title": title,
        "aprobado": False
    }
