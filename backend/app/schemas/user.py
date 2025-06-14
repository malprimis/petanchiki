import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.db.base import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: uuid.UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None


class UserInDB(UserRead):
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: uuid.UUID | None = None
