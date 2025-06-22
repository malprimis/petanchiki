import uuid
from datetime import datetime

from pydantic import BaseModel

from app.db.base import TransactionType


class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: str
    date: datetime
    category_id: uuid.UUID
    group_id: uuid.UUID


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TransactionUpdate(BaseModel):
    amount: float | None = None
    type: TransactionType | None = None
    description: str | None = None
    date: datetime | None = None
    category_id: uuid.UUID | None = None
