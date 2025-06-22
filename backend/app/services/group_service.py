import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import GroupRole
from app.models.group import Group
from app.models.user import User
from app.models.user_group import UserGroup
from app.schemas.group import GroupCreate, GroupUpdate
from app.services.user_service import get_user_by_email


async def create_group(
        db: AsyncSession,
        group_in: GroupCreate,
        owner_id: uuid.UUID
) -> Group:
    """
    Создаёт новую группу и добавляет владельца как администратора.

    :param db: асинхронная сессия SQLAlchemy
    :param group_in: данные о новой группе
    :param owner_id: UUID владельца группы
    :return: созданная группа
    """
    group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=owner_id,
        is_active=True,
        deleted_at=None
    )

    db.add(group)
    await db.commit()

    group = await get_group_by_id(db, group.id)

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
) -> Group | None:
    """
    Возвращает группу по её ID, опционально фильтруя по активности.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: UUID группы
    :param only_active: учитывать только активные группы
    :return: объект группы или None
    """
    stmt = select(Group).options(selectinload(Group.members))
    if only_active:
        stmt = stmt.filter(Group.is_active == True)
    stmt = stmt.filter(Group.id == group_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_group_by_user(
        db: AsyncSession,
        user_id: uuid.UUID
) -> Sequence[Group]:
    """
    Возвращает список активных групп, в которых состоит пользователь.

    :param db: асинхронная сессия SQLAlchemy
    :param user_id: UUID пользователя
    :return: список групп
    """
    stmt = (
        select(Group)
        .join(UserGroup, UserGroup.group_id == Group.id)
        .filter(UserGroup.user_id == user_id, Group.is_active == True)
        .options(selectinload(Group.members))
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def update_group(
        db: AsyncSession,
        group: Group,
        group_in: GroupUpdate,
        current_user: User
) -> Group:
    """
    Обновляет данные группы, если пользователь является её администратором.

    :param db: асинхронная сессия SQLAlchemy
    :param group: объект группы для обновления
    :param group_in: данные для обновления
    :param current_user: пользователь, совершающий операцию
    :return: обновлённая группа
    :raises HTTPException 403: если нет прав на обновление
    """
    membership = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group.id, UserGroup.user_id == current_user.id)
    )
    mem = membership.scalars().first()
    if not mem or mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail="forbidden")

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
    """
    Деактивирует (soft delete) группу. Может выполнить только владелец или глобальный админ.

    :param db: асинхронная сессия SQLAlchemy
    :param group: объект группы
    :param current_user: текущий пользователь
    :raises HTTPException 403: если нет прав на удаление
    """
    if group.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="forbidden")

    group.is_active = False
    group.deleted_at = datetime.now()
    await db.commit()


async def add_user_to_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        email: str,
        role: GroupRole = GroupRole.member
) -> UserGroup:
    """
    Добавляет пользователя в группу по email.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: ID группы
    :param email: email пользователя
    :param role: роль в группе (по умолчанию участник)
    :return: объект связи UserGroup
    :raises HTTPException 404: если группа или пользователь не найдены
    :raises HTTPException 400: если пользователь уже состоит в группе
    """
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    user = await get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    exists_stmt = await db.execute(
        select(UserGroup).filter(UserGroup.user_id == user.id, UserGroup.group_id == group_id)
    )
    exists = exists_stmt.scalars().first()

    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    membership = UserGroup(
        group_id=group_id,
        user_id=user.id,
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
    """
    Удаляет пользователя из группы, если текущий пользователь — администратор группы.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: UUID группы
    :param user_id: UUID удаляемого пользователя
    :param current_user: текущий пользователь (для проверки прав)
    :raises HTTPException 403: если нет прав
    """
    mem_check = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == current_user.id)
    )

    mem = mem_check.scalars().first()
    if not mem or mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail="forbidden")

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
    """
    Изменяет роль пользователя в группе.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: UUID группы
    :param user_id: UUID пользователя
    :param new_role: новая роль (admin/member)
    :param current_user: текущий пользователь (должен быть администратором)
    :return: обновлённый объект UserGroup
    :raises HTTPException 403: если нет прав
    :raises HTTPException 404: если пользователь не найден в группе
    """
    mem_check = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == current_user.id)
    )

    admin_mem = mem_check.scalars().first()

    if not admin_mem or admin_mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail="forbidden")

    stmt = (
        update(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
        .values(role=new_role)
        .returning(UserGroup)
    )
    result = await db.execute(stmt)
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="User not found")

    await db.commit()
    return membership


async def list_group_members(
        db: AsyncSession,
        group_id: uuid.UUID
) -> Sequence[UserGroup]:
    """
    Возвращает список участников группы.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: UUID группы
    :return: список объектов UserGroup
    """
    result = await db.execute(
        select(UserGroup).filter(UserGroup.group_id == group_id)
    )
    return result.scalars().all()


async def is_user_admin_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID
) -> bool:
    """
    Проверяет, является ли пользователь администратором группы.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: UUID группы
    :param user_id: UUID пользователя
    :return: True, если пользователь — администратор, иначе False
    """
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
    """
    Проверяет, состоит ли пользователь в группе.

    :param db: асинхронная сессия SQLAlchemy
    :param group_id: UUID группы
    :param user_id: UUID пользователя
    :return: True, если пользователь состоит в группе, иначе False
    """
    result = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    return bool(result.scalars().first())