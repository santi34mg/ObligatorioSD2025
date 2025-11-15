from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Material types according to MER
MaterialType = Literal[
    "Parcial de semestre anterior",
    "Examen de semestre anterior",
    "Apuntes",
    "Práctico"
]

# File formats according to MER
FileFormat = Literal[
    "pdf", "jpg", "png", "docx", "pptx", "xlsx", 
    "py", "java", "mp3", "mp4", "txt"
]


class MaterialCreate(BaseModel):
    """Schema for creating a material"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    tipo: Optional[MaterialType] = None
    id_asignatura: Optional[str] = None  # Will be required later


class MaterialInDB(BaseModel):
    """Material as stored in MongoDB"""
    id: str  # ObjectId as string
    filename: str
    title: str
    description: str
    url: str
    content_type: str
    uploader: str
    fecha_subida: datetime
    tipo: Optional[MaterialType] = None
    formato: Optional[FileFormat] = None
    tamaño: Optional[int] = None  # in bytes
    aprobado: bool = False
    id_asignatura: Optional[str] = None
    id_usuario: Optional[str] = None

    class Config:
        from_attributes = True


class PostUser(BaseModel):
    """User info for Post format (frontend expects this)"""
    name: str
    avatar: str


class PostResponse(BaseModel):
    """Response format matching frontend Post interface"""
    id: int  # Frontend expects number, we'll use hash or index
    user: PostUser
    date: datetime
    content: str  # This will be description or title+description
    commentCount: int = 0
    likes: int = 0
    image: Optional[str] = None  # Will be the file URL if it's an image


class MaterialResponse(BaseModel):
    """Material response for API"""
    id: str
    title: str
    description: str
    url: str
    filename: str
    uploader: str
    fecha_subida: datetime
    tipo: Optional[MaterialType] = None
    formato: Optional[FileFormat] = None
    tamaño: Optional[int] = None
    aprobado: bool = False
    content_type: str

    class Config:
        from_attributes = True


class MaterialListResponse(BaseModel):
    """Response for list of materials"""
    materials: list[MaterialResponse]
    total: int
    page: int = 1
    page_size: int = 20


class PostListResponse(BaseModel):
    """Response for posts (frontend format)"""
    posts: list[PostResponse]
    total: int

