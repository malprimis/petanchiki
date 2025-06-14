import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.user import Base, User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    delete_user,
)
from sqlalchemy import select

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture
async def async_session():
    # подготовка схемы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # сам Session
    async with AsyncSessionLocal() as session:
        yield session

# 2. Пример теста создания пользователя
@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_get_user(async_session):
    user_in = UserCreate(email="test@example.com", name="Test User", password="password123")
    user = await create_user(async_session, user_in)
    assert user.email == user_in.email
    assert user.name == user_in.name
    assert user.password_hash != "password123"

    fetched = await get_user_by_email(async_session, user_in.email)
    assert fetched is not None
    assert fetched.id == user.id

    fetched_by_id = await get_user_by_id(async_session, user.id)
    assert fetched_by_id is not None
    assert fetched_by_id.email == user.email

# 3. Пример теста обновления пользователя
@pytest.mark.asyncio(loop_scope="session")
async def test_update_user(async_session):
    user_in = UserCreate(email="upd@example.com", name="Updater", password="password123")
    user = await create_user(async_session, user_in)
    update_in = UserUpdate(name="New Name", password="newpassword456")
    # current_user = сам user (разрешим себе менять себя)
    user = await update_user(async_session, user, update_in, user)
    assert user.name == "New Name"
    assert user.password_hash != "password123"

# 4. Пример теста удаления пользователя
@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(async_session):
    user_in = UserCreate(email="del@example.com", name="Deleter", password="password123")
    user = await create_user(async_session, user_in)
    # current_user = сам user (может удалять себя)
    await delete_user(async_session, user, user)
    # После soft-delete: is_active == False, deleted_at не None
    fetched = await get_user_by_id(async_session, user.id)
    assert fetched is None
    # Но можно получить напрямую (если написать get_user_by_id_any)
    result = await async_session.execute(
        select(User).where(User.id == user.id)
    )
    deleted = result.scalars().first()
    assert deleted is not None
    assert deleted.is_active is False
    assert deleted.deleted_at is not None
