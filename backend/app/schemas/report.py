from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


class ReportPdfRequest(BaseModel):
    group_id: UUID
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    by_category: bool = False
    by_user: bool = False
    requested_by: Optional[UUID] = None

    model_config = SettingsConfigDict(
        json_schema_extra={
            "example": {
                "group_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "date_from": "2025-06-01",
                "date_to": "2025-06-30",
                "by_category": True,
                "by_user": True,
                "requested_by": "c56a4180-65aa-42ec-a945-5fd21dec0538"
            }
        }
    )


class ReportPdfData(BaseModel):
    by_category: Optional[dict[str, float]] = None
    by_user: Optional[dict[str, float]] = None
    total_expense: float
    total_income: float

    model_config = SettingsConfigDict(
        json_schema_extra={
            "example": {
                "by_category": {"Salary": 1000.0},
                "by_user": {"Reporter": 500.0},
                "total_expense": 500.0,
                "total_income": 1000.0
            }
        }
    )
