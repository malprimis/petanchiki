from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from app.db.session import get_db
from app.services.user_service import (
    create_user,
    svc_get_user as svc_get_user,
    list_users,
    update_user,
    delete_user,
)
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate
)
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    '/',
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new user'
)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await create_user(db, user_in)
    return user


@router.get(
    '/',
    response_model=list[UserRead],
    summary='List all users (admin-only)'
)
async def list_users_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough rights'
        )
    return await list_users(db)


@router.get(
    '/me',
    response_model=UserRead,
    summary='Get current user'
)
async def read_own_profile(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user


@router.get(
    '/{user_id}',
    response_model=UserRead,
    summary='Get user by ID'
)
async def get_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user = await svc_get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough rights')
    return user


@router.patch(
    '/{user_id}',
    response_model=UserRead,
    summary='Update user'
)
async def update_user_endpoint(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user = await svc_get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    updated = await update_user(db, user, user_in, current_user)
    return updated


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete (deactivate) user'
)
async def delete_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user = await svc_get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    await delete_user(db, user, current_user)
    return