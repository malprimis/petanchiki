import uuid
from datetime import datetime

from pydantic import BaseModel


class ReportRequest(BaseModel):
    group_id: uuid.UUID
    date_from: datetime | None = None
    date_to: datetime | None = None
    category_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class CategorySummary(BaseModel):
    category_id: uuid.UUID
    category_name: str
    total: float

class UserSummary(BaseModel):
    user_id: uuid.UUID
    user_name: str
    total: float
