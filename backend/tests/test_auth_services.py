import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.core.config import settings
from app.schemas.user import UserCreate
from app.services.auth_service import (
    verify_password,
    get_password_hash,
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    refresh_access_token,
    change_password,
)

# Настройка тестовой in-memory БД
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Параметры JWT из конфига
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

@pytest_asyncio.fixture()
async def async_session():
    # Пересоздаём схему перед каждым тестом
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session

def test_password_hash_and_verify():
    pw = "S3cr3tP@ss"
    h = get_password_hash(pw)
    assert h != pw
    assert verify_password(pw, h)
    assert not verify_password("wrong", h)

@pytest.mark.asyncio
async def test_register_and_duplicate(async_session: AsyncSession):
    uc = UserCreate(email="alice@example.com", name="Alice", password="password123")
    user = await register_user(async_session, uc)
    assert user.email == uc.email

    # повторная регистрация тем же email приводит к 409
    with pytest.raises(HTTPException) as exc:
        await register_user(async_session, uc)
    assert exc.value.status_code == status.HTTP_409_CONFLICT

@pytest.mark.asyncio
async def test_authenticate_user(async_session: AsyncSession):
    uc = UserCreate(email="bob@example.com", name="Bob", password="mypassword")
    await register_user(async_session, uc)

    ok = await authenticate_user(async_session, uc.email, uc.password)
    assert ok is not None
    assert ok.email == uc.email

    no_user = await authenticate_user(async_session, uc.email, "invalid")
    assert no_user is None

    no_user2 = await authenticate_user(async_session, "noone@example.com", "whatever")
    assert no_user2 is None

@pytest.mark.asyncio
async def test_jwt_token_and_current_user(async_session: AsyncSession):
    uc = UserCreate(email="carol@example.com", name="Carol", password="pass1234")
    user = await register_user(async_session, uc)

    # создаём токен с subject = str(user.id)
    token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=1))
    assert isinstance(token, str)

    # decode и получить пользователя
    current = await get_current_user(async_session, token)
    assert current.id == user.id

    # плохой токен
    with pytest.raises(HTTPException) as exc2:
        await get_current_user(async_session, token + "corrupt")
    assert exc2.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_refresh_access_token(async_session: AsyncSession):
    uc = UserCreate(email="dave@example.com", name="Dave", password="pass4321")
    user = await register_user(async_session, uc)

    old_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(seconds=0))
    # делаем expired token, но refresh проигнорирует exp
    new_token = await refresh_access_token(async_session, old_token)
    assert new_token != old_token

    # новый токен действителен
    current = await get_current_user(async_session, new_token)
    assert current.id == user.id

    # несуществующий пользователь
    fake = create_access_token(data={"sub": str(uuid.uuid4())})
    with pytest.raises(HTTPException) as exc3:
        await refresh_access_token(async_session, fake)
    assert exc3.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_change_password(async_session: AsyncSession):
    uc = UserCreate(email="eve@example.com", name="Eve", password="OrigPass123")
    user = await register_user(async_session, uc)

    # неправильный старый пароль
    with pytest.raises(HTTPException) as exc_bad:
        await change_password(async_session, user, current_password="wrong", new_password="NewPass123")
    assert exc_bad.value.status_code == status.HTTP_403_FORBIDDEN

    # успешная смена
    await change_password(async_session, user, current_password=uc.password, new_password="Complex1")
    # старый парроль больше не валиден
    assert await authenticate_user(async_session, uc.email, uc.password) is None
    # новый проходит
    assert (await authenticate_user(async_session, uc.email, "Complex1")).id == user.id
