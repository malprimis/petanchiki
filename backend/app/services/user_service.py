import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.utils import check_rights

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    password_hash = pwd_context.hash(user.password)
    user = User(email=user.email, name=user.name, password_hash=password_hash)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter(User.email == email, User.is_active == True))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).filter(User.id == id, User.is_active == True))
    return result.scalars().first()


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate, current_user: User) -> User:
    updated = False

    if not check_rights(current_user, user):
        raise HTTPException(status_code=403, detail='forbidden')

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


async def delete_user(db: AsyncSession, user: User, current_user: User):
    if user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    user.is_active = False
    user.deleted_at = datetime.now()
    await db.commit()
    return None


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    result = await db.execute(
        select(User).where(User.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()
