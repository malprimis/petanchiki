import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.models.user import User
from app.services.user_service import (
    get_user_by_email,
    get_user_by_id,
    create_user as create_user_in_db,
)
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def register_user(
        db: AsyncSession,
        user_in: UserCreate
) -> User:
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return await create_user_in_db(db, user_in)


async def authenticate_user(
        db: AsyncSession,
        email: EmailStr,
        password: str
) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    now = datetime.now()
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    db: AsyncSession = Depends(...),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        raw = payload.get("sub")
        user_id = uuid.UUID(raw)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception
    return user


async def refresh_access_token(
        db: AsyncSession,
        token: str
) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        raw = payload.get("sub")
        user_id = uuid.UUID(raw)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not await get_user_by_id(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return create_access_token(data={"sub": str(user_id)})


async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
) -> None:
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current password is incorrect"
        )

    user.password_hash = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)
