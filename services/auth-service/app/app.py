from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Literal
import uuid

from app.db import User, create_db_and_tables, get_async_session
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, current_admin_user, fastapi_users
from shared.rabbitmq_client import create_rabbitmq_client, EventPublisher
from shared.rabbitmq_config import SystemEvents
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/api/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)


# Role update schema
class RoleUpdate(BaseModel):
    role: Literal["student", "admin"]


@app.patch("/api/users/{user_id}/role", response_model=UserRead, tags=["admin"])
async def update_user_role(
    user_id: uuid.UUID,
    role_data: RoleUpdate,
    current_user: User = Depends(current_admin_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update a user's role. Only admins can perform this action.
    """
    # Find the user to update
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Update the role
    user.role = role_data.role
    await session.commit()
    await session.refresh(user)
    
    # Publish event if available
    global event_publisher
    if event_publisher:
        await event_publisher.publish_event(
            "user.role_updated",
            {
                "user_id": str(user.id),
                "email": user.email,
                "new_role": role_data.role,
                "updated_by": str(current_user.id)
            }
        )
    
    return UserRead.model_validate(user)


@app.get("/api/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    global event_publisher
    
    # Publicar evento de usuario autenticado 
    if event_publisher:
        await event_publisher.publish_user_login({
            "user_id": str(user.id),
            "email": user.email,
            "action": "authenticated_access"
        })
    
    return {"message": f"Hello {user.email}!"}

@app.post("/api/auth/register-with-events")
async def register_with_events(user_data: UserCreate):
    """Endpoint de ejemplo que registra usuario y publica evento"""
    global event_publisher
    
    # Aquí normalmente crearías el usuario en la base de datos
    # Por ahora simulamos el registro
    user_id = "user-123"
    
    # Publicar evento de usuario registrado 
    if event_publisher:
        await event_publisher.publish_user_registered({
            "user_id": user_id,
            "email": user_data.email,
            "action": "registration_completed"
        })
    
    return {"message": "Usuario registrado y evento publicado", "email": user_data.email}


# Cliente RabbitMQ global
rabbitmq_client = None
event_publisher = None

@app.on_event("startup")
async def on_startup():
    global rabbitmq_client, event_publisher
    
    await create_db_and_tables()
    
    # Conectar a RabbitMQ (con manejo de errores)
    try:
        rabbitmq_client = create_rabbitmq_client("auth-service")
        await rabbitmq_client.connect()
        event_publisher = EventPublisher(rabbitmq_client)
        
        # Configurar consumers para eventos que este servicio debe escuchar
        await rabbitmq_client.consume_events(
            [SystemEvents.MODERATION_APPROVED, SystemEvents.MODERATION_REJECTED],
            handle_moderation_event
        )
        print("✓ Auth service conectado a RabbitMQ")
    except Exception as e:
        print(f"⚠ Warning: No se pudo conectar a RabbitMQ: {e}")
        print("⚠ El servicio continuará sin eventos asíncronos")
        rabbitmq_client = None
        event_publisher = None

@app.on_event("shutdown")
async def on_shutdown():
    global rabbitmq_client
    
    # Desconectar de RabbitMQ
    if rabbitmq_client:
        await rabbitmq_client.disconnect()

async def handle_moderation_event(event_type: str, event_data: dict):
    """Manejar eventos de moderación"""
    print(f"Auth Service recibió evento de moderación: {event_type}")
    print(f"Datos: {event_data.get('data', {})}")
