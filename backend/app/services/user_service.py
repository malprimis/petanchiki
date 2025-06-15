from __future__ import annotations

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

__all__ = [
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "update_user",
    "delete_user",
    "list_users",
]

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Persist a new **active** user with a securely hashed password.

    Parameters
    ----------
    db:
        Live async SQLAlchemy session (usually provided by a FastAPI dependency).
    user:
        Pydantic model containing the *email*, *name* and raw *password*
        supplied by the client at registration time.

    Returns
    -------
    User
        Refreshed ORM instance holding an auto‑generated ``id`` and the
        *bcrypt*‑hashed password in ``password_hash``.

    Raises
    ------
    sqlalchemy.exc.SQLAlchemyError
        Bubbles up intact if database insertion fails.
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


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Return the *active* user whose e‑mail matches ``email``.

    Parameters
    ----------
    db
        Async session.
    email
        E‑mail address to look up (case‑sensitive matching).

    Returns
    -------
    User | None
        The matching ORM instance **or** *None* when no active user exists with
        that address.
    """
    result = await db.execute(
        select(User).filter(User.email == email, User.is_active == True)
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, id: uuid.UUID) -> User | None:
    """Retrieve an *active* user by primary key.

    Parameters
    ----------
    db
        Async session.
    id
        UUID primary key.

    Returns
    -------
    User | None
        ORM instance or *None* if user is absent/inactive.
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
    """Patch the user’s *mutable* fields: ``name`` and ``password``.

    Access Control
    --------------
    * The **user himself** may update their profile.
    * A **platform super‑admin** (``current_user.is_admin``) may update anyone.

    Validation Rules
    ---------------
    * ``name`` – must be ≥ *3* non‑whitespace characters (when provided).
    * ``password`` – at least *8* characters.

    Parameters
    ----------
    db, user, user_in, current_user
        See signature. ``user`` is an already attached ORM instance.

    Returns
    -------
    User
        Refreshed an ORM object after commit (or unchanged if nothing mutated).

    Raises
    ------
    fastapi.HTTPException
        * 403 – Caller lacks rights (delegated to `app.utils.utils.check_rights`).
        * 422 – Validation failures for *name* or *password*.
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


async def delete_user(db: AsyncSession, user: User, current_user: User) -> None:
    """Soft‑delete a user (``is_active=False`` + tombstone timestamp).

    Authorisation matrix mirrors `update_user` – self‑deleting or
    admin‑initiated deletions are allowed.

    Parameters
    ----------
    db, user, current_user
        See signature.

    Raises
    ------
    fastapi.HTTPException
        * 403 – When neither self‑delete nor admin‑delete conditions are met.
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
    """Return a **paginated** list of *active* users.

    Parameters
    ----------
    db
        Async session.
    skip
        Offset for result pagination ("page start").
    limit
        Maximum number of users to return. Hard cap is delegated to the caller
        (router/endpoint) – default *100*.

    Returns
    -------
    Sequence[User]
        List‑like collection of ORM instances.
    """
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
