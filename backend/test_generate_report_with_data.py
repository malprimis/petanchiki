# test_generate_report_with_data.py

import asyncio
from uuid import uuid4
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import date as dt_date, datetime, timedelta
from app.models.user import User
from app.models.group import Group
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.report import ReportRequest
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
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Тестовый пользователь",
        password_hash="fakehash1234",
        is_active=True,
        role="user"
    )
    db.add(user)

    # Группа
    group = Group(
        id=uuid4(),
        name="Тестовая группа",
        description="Группа для тестирования отчётов",
        owner_id=user.id,
        is_active=True
    )
    db.add(group)

    # Категории
    categories = [
        Category(id=uuid4(), group_id=group.id, name="Продукты"),
        Category(id=uuid4(), group_id=group.id, name="Кафе"),
        Category(id=uuid4(), group_id=group.id, name="Развлечения")
    ]
    db.add_all(categories)
    await db.flush()

    # Транзакции
    transactions = []
    for i in range(10):
        tx = Transaction(
            id=uuid4(),
            group_id=group.id,
            category_id=categories[i % len(categories)].id,
            user_id=user.id,
            amount=round(100 + i * 50, 2),
            type="expense" if i % 2 == 0 else "income",
            description=f"Покупка #{i}",
            date=dt_date.today() - timedelta(days=i)
        )
        transactions.append(tx)

    db.add_all(transactions)
    await db.commit()

    return {
        "user": user,
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

        from app.schemas.report import ReportRequest

        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        req = ReportRequest(
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