from datetime import datetime, timedelta
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base, TransactionType, GroupRole
from app.schemas.category import CategoryCreate
from app.schemas.group import GroupCreate
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.schemas.user import UserCreate
from app.services.category_service import create_category
from app.services.group_service import create_group, add_user_to_group, change_user_role_in_group
from app.services.transaction_service import (
    create_transaction,
    get_transaction_by_id,
    list_transactions,
    update_transaction,
    delete_transaction,
    check_transaction_permission
)
from app.services.user_service import create_user

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def async_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session

@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_get_transaction(async_session: AsyncSession):
    # Setup: user, group, category
    user = await create_user(async_session, UserCreate(email="txuser@example.com", name="TXUser", password="pass1234"))
    group = await create_group(async_session, GroupCreate(name="TX Group", description=""), user.id)
    category = await create_category(async_session, CategoryCreate(name="Food", icon=""), group.id)
    # Create transaction
    now = datetime.now()
    tx_in = TransactionCreate(
        group_id=group.id,
        category_id=category.id,
        amount=100.0,
        type=TransactionType.expense,
        description="Lunch",
        date=now
    )
    tx = await create_transaction(async_session, tx_in, user.id)
    assert isinstance(tx.id, UUID)
    assert tx.amount == 100.0
    assert tx.type == TransactionType.expense
    assert tx.description == "Lunch"
    assert tx.date == now
    # Get by ID
    fetched = await get_transaction_by_id(async_session, tx.id)
    assert fetched.id == tx.id

@pytest.mark.asyncio(loop_scope="session")
async def test_list_transactions_with_filters(async_session: AsyncSession):
    user = await create_user(async_session, UserCreate(email="listuser@example.com", name="ListUser", password="pass1234"))
    group = await create_group(async_session, GroupCreate(name="List Group", description=""), user.id)
    cat1 = await create_category(async_session, CategoryCreate(name="Food", icon=""), group.id)
    cat2 = await create_category(async_session, CategoryCreate(name="Travel", icon=""), group.id)
    # Create multiple transactions
    dt = datetime.now()
    tx1 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id, category_id=cat1.id, amount=50.0,
        type=TransactionType.expense, description="Dinner", date=dt - timedelta(days=1)
    ), user.id)
    tx2 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id, category_id=cat2.id, amount=200.0,
        type=TransactionType.expense, description="Taxi", date=dt
    ), user.id)
    # List all
    all_txs = await list_transactions(async_session, group.id)
    assert {t.id for t in all_txs} == {tx1.id, tx2.id}
    # Filter by category
    food_txs = await list_transactions(async_session, group.id, category_id=cat1.id)
    assert [t.id for t in food_txs] == [tx1.id]
    # Filter by date range
    today_txs = await list_transactions(async_session, group.id, date_from=dt)
    assert [t.id for t in today_txs] == [tx2.id]

@pytest.mark.asyncio(loop_scope="session")
async def test_update_and_delete_transaction(async_session: AsyncSession):
    user = await create_user(async_session, UserCreate(email="updel@example.com", name="UpDel", password="pass1234"))
    group = await create_group(async_session, GroupCreate(name="UpDel Group", description=""), user.id)
    category = await create_category(async_session, CategoryCreate(name="Bills", icon=""), group.id)
    tx = await create_transaction(async_session, TransactionCreate(
        group_id=group.id, category_id=category.id,
        amount=75.0, type=TransactionType.expense, description="Electricity", date=datetime.now()
    ), user.id)
    # Update
    new_dt = datetime.now()
    tx = await update_transaction(async_session, tx, TransactionUpdate(
        amount=80.0, description="Electric", date=new_dt
    ), user.id)
    assert tx.amount == 80.0
    assert tx.description == "Electric"
    assert tx.date == new_dt
    # Delete
    await delete_transaction(async_session, tx, user.id)
    deleted = await get_transaction_by_id(async_session, tx.id)
    assert deleted is None

@pytest.mark.asyncio(loop_scope="session")
async def test_transaction_permission(async_session: AsyncSession):
    owner = await create_user(async_session, UserCreate(email="perm1@example.com", name="Perm1", password="pass1234"))
    other = await create_user(async_session, UserCreate(email="perm2@example.com", name="Perm2", password="pass1234"))
    group = await create_group(async_session, GroupCreate(name="Perm Group", description=""), owner.id)
    category = await create_category(async_session, CategoryCreate(name="Misc", icon=""), group.id)
    tx = await create_transaction(async_session, TransactionCreate(
        group_id=group.id, category_id=category.id,
        amount=30.0, type=TransactionType.expense, description="Test", date=datetime.now()
    ), owner.id)
    # Owner can edit/delete
    assert await check_transaction_permission(async_session, tx, owner.id)
    # Other (not in a group) cannot
    assert not await check_transaction_permission(async_session, tx, other.id)
    # Add other as member
    await add_user_to_group(async_session, group.id, other.email)
    assert await check_transaction_permission(async_session, tx, other.id) == False
    # Promote to admin
    await change_user_role_in_group(async_session, group.id, other.id, new_role=GroupRole.admin, current_user=owner)
    assert await check_transaction_permission(async_session, tx, other.id) == True
