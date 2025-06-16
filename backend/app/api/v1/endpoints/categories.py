from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.category_service import (
    create_category as svc_create_category,
    get_category_by_id as svc_get_category,
    list_categories_for_group as svc_list_categories,
    update_category as svc_update_category,
    delete_category as svc_delete_category,
)
from app.services.group_service import is_user_member_in_group
from app.services.auth_service import get_current_user
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.models.user import User

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    '/groups/{group_id}/categories',
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category in a group",
)
async def create_category():
    pass