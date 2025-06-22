from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.group import GroupCreate
from app.schemas.user import UserCreate
from app.services.category_service import (
    create_category,
    get_category_by_id,
    list_categories_for_group,
    update_category,
    delete_category,
    is_category_name_unique,
)
from app.services.group_service import create_group
from app.services.user_service import create_user

# тестовая БД в памяти
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture
async def async_session():
    # пересоздаём схему перед каждым тестом
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session

@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_get_list_category(async_session: AsyncSession):
    # подготовка: создаём пользователя и группу
    user = await create_user(async_session,
        UserCreate(email="catuser@example.com", name="CatUser", password="pass1234")
    )
    group = await create_group(async_session,
        GroupCreate(name="Cat Group", description=""),
        user.id
    )

    # создаём категорию
    cat_in = CategoryCreate(name="Food", icon="🍔")
    category = await create_category(async_session, cat_in, group.id)
    assert isinstance(category.id, UUID)
    assert category.name == "Food"
    assert category.icon == "🍔"
    assert category.group_id == group.id

    # get by id
    fetched = await get_category_by_id(async_session, category.id)
    assert fetched is not None
    assert fetched.id == category.id

    # list for a group
    lst = await list_categories_for_group(async_session, group.id)
    assert len(lst) == 1
    assert lst[0].id == category.id

@pytest.mark.asyncio(loop_scope="session")
async def test_unique_name(async_session: AsyncSession):
    # подготовка: пользователь и группа
    user = await create_user(async_session,
        UserCreate(email="dupuser@example.com", name="DupUser", password="pass1234")
    )
    group = await create_group(async_session,
        GroupCreate(name="Dup Group", description=""),
        user.id
    )

    # первая категория
    await create_category(async_session, CategoryCreate(name="Rent", icon="🏠"), group.id)
    # попытка создать вторую с таким же именем
    with pytest.raises(HTTPException) as exc:
        await create_category(async_session, CategoryCreate(name="Rent", icon="🏠"), group.id)
    assert exc.value.status_code == 400

    # is_category_name_unique
    assert not await is_category_name_unique(async_session, group.id, "Rent")
    assert await is_category_name_unique(async_session, group.id, "Utilities")

@pytest.mark.asyncio(loop_scope="session")
async def test_update_category(async_session: AsyncSession):
    # подготовка
    user = await create_user(async_session,
        UserCreate(email="updcat@example.com", name="UpdCat", password="pass1234")
    )
    group = await create_group(async_session,
        GroupCreate(name="Upd Group", description=""),
        user.id
    )
    category = await create_category(async_session, CategoryCreate(name="Books", icon="📚"), group.id)

    # обновляем имя и иконку
    upd = await update_category(async_session, category, CategoryUpdate(name="Novels", icon="📖"))
    assert upd.name == "Novels"
    assert upd.icon == "📖"

    # попытка переименовать в уже существующее
    await create_category(async_session, CategoryCreate(name="Magazines", icon="📰"), group.id)
    with pytest.raises(HTTPException):
        await update_category(async_session, upd, CategoryUpdate(name="Magazines"))

@pytest.mark.asyncio(loop_scope="session")
async def test_delete_category(async_session: AsyncSession):
    # подготовка
    user = await create_user(async_session,
        UserCreate(email="delcat@example.com", name="DelCat", password="pass1234")
    )
    group = await create_group(async_session,
        GroupCreate(name="Del Group", description=""),
        user.id
    )
    category = await create_category(async_session, CategoryCreate(name="Sport", icon="🏀"), group.id)

    # удаляем
    await delete_category(async_session, category)
    # после удаления get вернёт None
    fetched = await get_category_by_id(async_session, category.id)
    assert fetched is None
