from __future__ import annotations

import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.utils import check_rights

__all__ = [
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "update_user",
    "delete_user",
    "list_users",
]

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(
        db: AsyncSession,
        user: UserCreate
) -> User:
    """
    Создаёт нового пользователя с хешированием пароля.

    :param db: асинхронная сессия SQLAlchemy
    :param user: данные для создания пользователя
    :return: созданный пользователь
    """
    password_hash = pwd_context.hash(user.password)
    user = User(
        email=user.email,
        name=user.name,
        password_hash=password_hash,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(
        db: AsyncSession,
        email: str | EmailStr
) -> User | None:
    """
    Получает активного пользователя по email.

    :param db: асинхронная сессия SQLAlchemy
    :param email: email пользователя
    :return: объект пользователя или None
    """
    result = await db.execute(
        select(User).filter(User.email == email, User.is_active == True)
    )
    return result.scalars().first()


async def get_user_by_id(
        db: AsyncSession,
        id: uuid.UUID
) -> User | None:
    """
    Получает активного пользователя по ID.

    :param db: асинхронная сессия SQLAlchemy
    :param id: UUID пользователя
    :return: объект пользователя или None
    """
    result = await db.execute(
        select(User).filter(User.id == id, User.is_active == True)
    )
    return result.scalars().first()


async def update_user(
        db: AsyncSession,
        user: User,
        user_in: UserUpdate,
        current_user: User,
) -> User:
    """
    Обновляет имя и/или пароль пользователя при наличии прав.

    :param db: асинхронная сессия SQLAlchemy
    :param user: пользователь, которого нужно обновить
    :param user_in: данные для обновления
    :param current_user: текущий пользователь (для проверки прав)
    :return: обновлённый пользователь
    :raises HTTPException 403: при отсутствии прав
    :raises HTTPException 422: если имя/пароль невалидны
    """
    updated = False

    if not check_rights(current_user, user):
        raise HTTPException(status_code=403, detail="forbidden")

    if user_in.name is not None and len(user_in.name.strip()) < 3:
        raise HTTPException(status_code=422, detail="Name too short")

    if user_in.password is not None and len(user_in.password) < 8:
        raise HTTPException(status_code=422, detail="Password too short")

    if user_in.name is not None:
        user.name = user_in.name
        updated = True

    if user_in.password is not None:
        user.password_hash = pwd_context.hash(user_in.password)
        updated = True

    if updated:
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(
        db: AsyncSession,
        user: User,
        current_user: User
) -> None:
    """
    Деактивирует пользователя (soft delete).

    :param db: асинхронная сессия SQLAlchemy
    :param user: пользователь, которого нужно удалить
    :param current_user: текущий пользователь (для проверки прав)
    :raises HTTPException 403: при отсутствии прав
    """
    if user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    user.is_active = False
    user.deleted_at = datetime.now()
    await db.commit()
    return None


async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
) -> Sequence[User]:
    """
    Возвращает список активных пользователей с пагинацией.

    :param db: асинхронная сессия SQLAlchemy
    :param skip: количество пропущенных записей
    :param limit: максимальное количество возвращаемых записей
    :return: список пользователей
    """
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
