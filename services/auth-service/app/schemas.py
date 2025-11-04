import uuid

from fastapi_users import schemas
from typing import Literal


class UserRead(schemas.BaseUser[uuid.UUID]):
    role: Literal["student", "admin"] = "student"


class UserCreate(schemas.BaseUserCreate):
    # Users register as students by default - no role selection during registration
    pass


class UserUpdate(schemas.BaseUserUpdate):
    # Regular users cannot update their own role
    pass
