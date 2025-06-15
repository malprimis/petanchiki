import uuid
from datetime import datetime
from typing import Any, Coroutine, Sequence

from sqlalchemy import select, delete, update, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.db.base import GroupRole
from app.models import UserGroup
from app.models.user import User
from app.models.group import Group
from app.models.user_group import UserGroup
from app.schemas.group import GroupCreate, GroupUpdate, UserGroupRead
from app.utils.utils import check_rights


async def create_group(
        db: AsyncSession,
        group_in: GroupCreate,
        owner_id: uuid.UUID
) -> Group:
    group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=owner_id,
        is_active=True,
        deleted_at=None
    )

    db.add(group)
    await db.commit()
    await db.refresh(group)

    membership = UserGroup(
        group_id=group.id,
        user_id=owner_id,
        role=GroupRole.admin,
        joined_at=datetime.now()
    )
    db.add(membership)
    await db.commit()
    return group


async def get_group_by_id(
        db: AsyncSession,
        group_id: uuid.UUID,
        only_active: bool = True
) -> Group:
    stmt = select(Group).filter(Group.id == group_id)
    if only_active:
        stmt = stmt.filter(Group.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_group_by_user(
        db: AsyncSession,
        user_id: uuid.UUID
) -> Sequence[Group]:
    stmt = (
        select(Group)
        .join(UserGroup, UserGroup.group_id == Group.id)
        .filter(UserGroup.user_id == user_id, Group.is_active == True)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def update_group(
        db: AsyncSession,
        group: Group,
        group_in: Group,
        current_user: User
) -> Group:
    membership = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group.id, UserGroup.user_id == current_user.id)
    )
    mem = membership.scalars().first()
    if not mem or mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail='forbidden')

    updated = False


    if group_in.name is not None:
        group.name = group_in.name
        updated = True

    if group_in.description is not None:
        group.description = group_in.description
        updated = True

    if updated:
        await db.commit()
        await db.refresh(group)

    return group


async def delete_group(
        db: AsyncSession,
        group: Group,
        current_user: User
) -> None:

    if group.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail='forbidden')

    group.is_active = False
    group.deleted_at = datetime.now()
    await db.commit()


async def add_user_to_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        role: GroupRole = GroupRole.member
) -> UserGroup:

    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    user_stmt = await db.execute(
        select(User)
        .filter(User.id == user_id, User.is_active == True)
    )
    user = user_stmt.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    exists_stmt = await db.execute(
        select(UserGroup)
        .filter(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
    )
    exists = exists_stmt.scalars().first()

    if exists:
        raise HTTPException(status_code=400, detail='User already exists')


    membership = UserGroup(
        group_id=group_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now()
    )

    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def remove_user_from_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: User
) -> None:

    mem_check = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == current_user.id)
    )

    mem = mem_check.scalars().first()
    if not mem or mem.role != GroupRole.admin:
        HTTPException(status_code=403, detail='forbidden')

    stmt = (
        delete(UserGroup)
        .filter(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
    )

    await db.execute(stmt)
    await db.commit()


async def change_user_role_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: GroupRole,
        current_user: User
) -> UserGroup:

    mem_check = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )

    admin_mem = mem_check.scalars().first()

    if not admin_mem or admin_mem.role != GroupRole.admin:
        HTTPException(status_code=403, detail='forbidden')

    stmt = (
        update(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
        .values(role=new_role)
        .returning(UserGroup)
    )
    result = await db.execute(stmt)
    membership = result.scalars().first()
    if not membership:
        HTTPException(status_code=404, detail='User not found')

    await db.commit()
    return membership


async def list_group_members(
        db: AsyncSession,
        group_id: uuid.UUID
) -> Sequence[UserGroup]:

    result = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id)
    )
    return result.scalars().all()


async def is_user_admin_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID
) -> bool:

    result = await db.execute(
        select(UserGroup.role)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    role = result.scalars().first()
    return role == GroupRole.admin


async def is_user_member_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID
) -> bool:

    result = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    return bool(result.scalars().first())

