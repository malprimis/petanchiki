import uuid
from datetime import datetime

from pydantic import BaseModel

from app.db.base import GroupRole
from user import UserRead


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


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class UserGroupBase(BaseModel):
    user_id: uuid.UUID
    group_id: uuid.UUID
    role: GroupRole
    joined_at: datetime


class UserGroupRead(UserGroupBase):
    id: uuid.UUID
