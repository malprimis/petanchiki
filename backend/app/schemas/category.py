import uuid
from datetime import datetime

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    icon: str | None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: uuid.UUID
    group_id: uuid.UUID
    created_at: datetime