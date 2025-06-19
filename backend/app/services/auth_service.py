# app/services/auth_service.py

import uuid
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.schemas.user import UserCreate
from app.models.user import User
from app.services.user_service import (
    create_user as create_user_in_db,
    get_user_by_email,
    get_user_by_id,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.config import settings


async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Регистрирует нового пользователя.

    Проверяет, что email ещё не зарегистрирован, затем создаёт запись в БД.

    :param db: асинхронная сессия SQLAlchemy
    :param user_in: данные нового пользователя
    :return: созданный объект User
    :raises HTTPException 409: если email уже существует
    """
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return await create_user_in_db(db, user_in)


async def authenticate_user(
        db: AsyncSession,
        email: EmailStr,
        password: str
) -> Optional[User]:
    """
    Аутентифицирует пользователя по email и паролю.

    :param db: Асинхронная сессия SQLAlchemy
    :param email: e-mail пользователя
    :param password: введённый пароль
    :return: объект User, если аутентификация успешна, иначе None
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def refresh_access_token(db: AsyncSession, token: str) -> str:
    """
    Обновляет access токен по истёкшему или почти истёкшему refresh токену.

    :param db: асинхронная сессия SQLAlchemy
    :param token: старый JWT токен
    :return: новый JWT токен
    :raises HTTPException 401: если токен некорректен
    :raises HTTPException 404: если пользователь не найден
    """
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
        raw = payload.get("sub")
        user_id = uuid.UUID(raw) if raw else None
    except (JWTError, ValueError, TypeError):
        raise credentials_error

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
) -> None:
    """
    Сменяет пароль пользователя.

    Проверяет старый пароль, проверяет сложность нового, хеширует его,
    сохраняет в БД.

    :param db: асинхронная сессия SQLAlchemy
    :param user: объект User, чей пароль меняем
    :param current_password: текущий (старый) пароль
    :param new_password: новый пароль
    :raises HTTPException 403: если старый пароль неверен
    :raises HTTPException 422: если новый пароль слишком простой
    """
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current password is incorrect")

    if len(new_password) < 8 or new_password.isalpha() or new_password.isdigit():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Password must contain letters and numbers")

    user.password_hash = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)
