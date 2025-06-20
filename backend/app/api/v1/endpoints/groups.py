from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.base import GroupRole
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.group import (
    GroupCreate,
    GroupRead,
    GroupUpdate,
    GroupAddUser,
    UserGroupRead,
)
from app.services.group_service import (
    create_group,
    get_group_by_id as svc_get_group,
    list_group_by_user,
    update_group as svc_update_group,
    delete_group as svc_delete_group,
    add_user_to_group as svc_add_user,
    remove_user_from_group as svc_remove_user,
    change_user_role_in_group as svc_change_role,
    list_group_members as svc_list_members,
)

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
)


@router.post(
    '/',
    response_model=GroupRead,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new group'
)
async def create_group_endpoint(
        group_in: GroupCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    group = await create_group(db, group_in, owner_id=current_user.id)
    return group


@router.get(
    '/',
    response_model=list[GroupRead],
    summary='List groups for current user'
)
async def list_my_group(
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    return await list_group_by_user(db, current_user.id)


@router.get(
    '/{group_id}',
    response_model=GroupRead,
    summary='Get group by id'
)
async def get_group(
        group_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    group = await svc_get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Group not found')

    is_member = any(m.user_id == current_user.id for m in await svc_list_members(db, group_id))
    if not is_member and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not enough rights')
    return group


@router.patch(
    '/{group_id}',
    response_model=GroupRead,
    summary='Update group'
)
async def update_group(
        group_id: UUID,
        group_in: GroupUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    group = await svc_get_group(db, group_id)

    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Group not found')

    updated = await svc_update_group(db, group, group_in, current_user)
    return updated


@router.delete(
    '/{group_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Delete (deactivate) group'
)
async def delete_group(
        group_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    group = await svc_get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Group not found')

    await svc_delete_group(db, group, current_user)
    return None


@router.post(
    '/{group_id}/members',
    response_model=UserGroupRead,
    status_code=status.HTTP_201_CREATED,
    summary='Add member to group'
)
async def add_member(
        group_id: UUID,
        payload: GroupAddUser,
        db: AsyncSession = Depends(get_db),
):
    membership = await svc_add_user(db, group_id, payload.email, payload.role)
    return membership


@router.get(
    '/{group_id}/members',
    response_model=list[UserGroupRead],
    summary='List all group members'
)
async def list_members(
        group_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    members = await svc_list_members(db, group_id)
    if not any(m.user_id == current_user.id for m in members):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a group member')
    return members


@router.patch(
    '/{group_id}/members/{user_id}',
    response_model=UserGroupRead,
    summary="Change member's role"
)
async def change_member_role(
        group_id: UUID,
        user_id: UUID,
        new_role: GroupRole,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    membership = await svc_change_role(db, group_id, user_id, new_role, current_user)

    return membership


@router.delete(
    '/{group_id}/members/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Remove a member from group'
)
async def remove_member(
        group_id: UUID,
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    await svc_remove_user(db, group_id, user_id, current_user)
    return None