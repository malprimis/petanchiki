import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.db.base import GroupRole
from app.schemas.user import UserRead


class GroupBase(BaseModel):
    name: str
    description: str


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    members: list['UserRead']
    is_active: bool
    deleted_at: datetime | None = None


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class GroupAddUser(BaseModel):
    email: EmailStr
    role: GroupRole = GroupRole.member


class UserGroupBase(BaseModel):
    user_id: uuid.UUID
    group_id: uuid.UUID
    role: GroupRole
    joined_at: datetime


class UserGroupRead(UserGroupBase):
    id: uuid.UUID
