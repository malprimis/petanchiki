# tests/test_report_service.py

import pytest
import pytest_asyncio
from datetime import datetime
from uuid import UUID

from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base, TransactionType
from app.schemas.user import UserCreate
from app.schemas.group import GroupCreate
from app.schemas.category import CategoryCreate
from app.schemas.transaction import TransactionCreate
from app.schemas.report import ReportRequest
from app.services.user_service import create_user
from app.services.group_service import create_group
from app.services.category_service import create_category
from app.services.transaction_service import create_transaction
from app.services.report_service import generate_report_data, generate_report_pdf, get_report_file_path


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
async def test_generate_report_data(async_session: AsyncSession):
    user = await create_user(async_session, UserCreate(email="repuser@example.com", name="Reporter", password="pass1234"))
    group = await create_group(async_session, GroupCreate(name="Report Group", description=""), owner_id=user.id)
    category = await create_category(async_session, CategoryCreate(name="Salary", icon="💰"), group_id=group.id)

    tx1 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id,
        category_id=category.id,
        amount=1000,
        type=TransactionType.income,
        description="Зарплата",
        date=datetime(2025, 1, 1)
    ), author_id=user.id)

    tx2 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id,
        category_id=category.id,
        amount=500,
        type=TransactionType.expense,
        description="Обед",
        date=datetime(2025, 1, 2)
    ), author_id=user.id)

    req = ReportRequest(group_id=group.id)
    data = await generate_report_data(async_session, req)

    assert data["income_total"] == 1000
    assert data["expense_total"] == 500
    assert data["balance"] == 500
    assert len(data["transactions"]) == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_report_pdf(async_session: AsyncSession):
    user = await create_user(async_session, UserCreate(email="pdfuser@example.com", name="PDFUser", password="pass1234"))
    group = await create_group(async_session, GroupCreate(name="PDF Group", description=""), owner_id=user.id)
    category = await create_category(async_session, CategoryCreate(name="Travel", icon="✈️"), group_id=group.id)

    tx1 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id,
        category_id=category.id,
        amount=100,
        type=TransactionType.expense,
        description="Проезд",
        date=datetime(2025, 1, 1)
    ), author_id=user.id)

    tx2 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id,
        category_id=category.id,
        amount=1000,
        type=TransactionType.income,
        description="Зарплата",
        date=datetime(2025, 1, 1)
    ), author_id=user.id)

    tx3 = await create_transaction(async_session, TransactionCreate(
        group_id=group.id,
        category_id=category.id,
        amount=500,
        type=TransactionType.expense,
        description="Обед",
        date=datetime(2025, 1, 2)
    ), author_id=user.id)

    req = ReportRequest(group_id=group.id)
    path = await generate_report_pdf(async_session, req)

    assert Path(path).exists()


@pytest.mark.asyncio(loop_scope="session")
async def test_get_report_file_path(async_session: AsyncSession):
    from uuid import uuid4
    with pytest.raises(FileNotFoundError):
        await get_report_file_path(uuid4())