from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import (
    create_category as svc_create_category,
    list_categories_for_group as svc_list_categories,
    get_category_by_id as svc_get_category_by_id,
    update_category as svc_update_category,
    delete_category as svc_delete_category,
)
from app.services.group_service import is_user_member_in_group

router = APIRouter(
    tags=["Categories"],
)


@router.post(
    '/groups/{group_id}/categories',
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category in a group",
)
async def create_category(
        group_id: UUID,
        payload: CategoryCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    if not await is_user_member_in_group(db, group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a group member')
    category = await svc_create_category(db, payload, group_id)
    return category


@router.get(
    '/groups/{group_id}/categories',
    response_model=list[CategoryRead],
    summary='List all categories in a group'
)
async def get_categories(
        group_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    if not await is_user_member_in_group(db, group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a group member')
    categories = await svc_list_categories(db, group_id)
    return categories


@router.patch(
    '/categories/{category_id}',
    response_model=CategoryUpdate,
    summary='Update category'
)
async def update_category_endpoint(
        category_id: UUID,
        payload: CategoryUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    category = await svc_get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    if not await is_user_member_in_group(db, category.group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a group member')

    return await svc_update_category(db, category, payload)


@router.delete(
    '/categories/{category_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete category'
)
async def delete_category_endpoint(
        category_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    category = await svc_get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    if not await is_user_member_in_group(db, category.group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a group member')

    await svc_delete_category(db, category)
    return None