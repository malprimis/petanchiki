# generate_report_with_data.py

import asyncio
import random
from uuid import uuid4
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import date as dt_date, datetime, timedelta
from app.db.base import TransactionType
from app.models.user import User
from app.models.group import Group
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.report import ReportPdfRequest
from app.services.report_service import generate_report_data, generate_report_pdf
from app.db.base import Base


# --- Подключение к БД (SQLite) ---
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def setup_test_data(db: AsyncSession) -> dict:
    """
    Создаёт тестовые данные для отчёта.
    """

    # Пользователь
    users = [
        User(
            id=uuid4(),
            email="test@example.com",
            name="Клоп",
            password_hash="fakehasasdh1234",
            is_active=True,
            role="user"
        ),
        User(
            id=uuid4(),
            email="test1@example.com",
            name="Лёша",
            password_hash="faasdkehash1234",
            is_active=True,
            role="user"
        ),
        User(
            id=uuid4(),
            email="test2@example.com",
            name="Паша",
            password_hash="fakedsadhash1234",
            is_active=True,
            role="user"
        ),
    ]
    db.add_all(users)

    # Группа
    group = Group(
        id=uuid4(),
        name="Тестовая группа",
        description="Группа для тестирования отчётов",
        owner_id=users[0].id,
        is_active=True
    )
    db.add(group)

    # Категории
    categories = [
        Category(id=uuid4(), group_id=group.id, name="Продукты"),
        Category(id=uuid4(), group_id=group.id, name="Кафе"),
        Category(id=uuid4(), group_id=group.id, name="Транспорт"),
        Category(id=uuid4(), group_id=group.id, name="Развлечения"),
        Category(id=uuid4(), group_id=group.id, name="Коммуналка"),
        Category(id=uuid4(), group_id=group.id, name="Связь"),
        Category(id=uuid4(), group_id=group.id, name="Медицина"),
        Category(id=uuid4(), group_id=group.id, name="Образование")
    ]
    db.add_all(categories)
    await db.flush()

    # Транзакции
    transactions = []
    for i in range(30):
        tx = Transaction(
            id=uuid4(),
            group_id=group.id,
            category_id=categories[i % len(categories)].id,
            user_id=users[i % len(users)].id,
            amount=round(100 + i * 50, 2),
            type=TransactionType.expense if random.randint(1, 101) % 2 == 0 else TransactionType.income,
            description=f"Покупка #{i}",
            date=dt_date.today() - timedelta(days=i)
        )
        transactions.append(tx)

    db.add_all(transactions)
    await db.commit()

    return {
        "user": users,
        "group": group,
        "transactions": transactions
    }


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("🚀 Начинаю создание тестовых данных...")
        data = await setup_test_data(db)
        print("✅ Тестовые данные созданы.")

        print("📊 Генерация данных отчёта...")

        from app.schemas.report import ReportPdfRequest

        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        req = ReportPdfRequest(
            group_id=data["group"].id,
            by_category=True,
            by_user=True,
            date_from=thirty_days_ago,
            date_to=today
        )

        report_data = await generate_report_data(db, req)
        print("📊 Данные отчёта:", report_data)

        print("📄 Генерация PDF-отчёта...")
        file_path = await generate_report_pdf(db, req)
        print(f"✅ Отчёт сохранён: {file_path}")


if __name__ == "__main__":
    asyncio.run(main())