import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

metadata = MetaData(schema="auth")
Base = declarative_base(metadata=metadata)


class User(Base):
    """
    User model that references the existing 'user' table created by auth-service.
    This is a read-only reference for querying user data.
    DO NOT create or modify this table from this service.
    """
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String, default="student", nullable=False)
