# backend/app/services/report_service.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from weasyprint import HTML
import tempfile
import os

from app.models.transaction import Transaction
from app.models.category import Category
from app.models.user import User
from app.schemas.report import ReportRequest
from app.db.base import TransactionType


async def generate_report_data(db: AsyncSession, req: ReportRequest) -> dict:
    """
    Генерирует агрегированные данные по транзакциям за указанный период.
    """
    stmt = (
        select(
            Transaction,
            Category.name.label("category_name"),
            User.name.label("user_name")
        )
        .join(Category, Transaction.category_id == Category.id)
        .join(User, Transaction.user_id == User.id)
        .filter(Transaction.group_id == req.group_id)
    )

    if req.start_date:
        stmt = stmt.filter(Transaction.date >= req.start_date)
    if req.end_date:
        stmt = stmt.filter(Transaction.date <= req.end_date)
    if req.user_id:
        stmt = stmt.filter(Transaction.user_id == req.user_id)
    if req.category_id:
        stmt = stmt.filter(Transaction.category_id == req.category_id)

    result = await db.execute(stmt)
    transactions = result.all()

    # Агрегация
    income_total = sum(t.Transaction.amount for t in transactions if t.Transaction.type == TransactionType.income)
    expense_total = sum(t.Transaction.amount for t in transactions if t.Transaction.type == TransactionType.expense)

    categories_summary = {}
    users_summary = {}

    for tx, category_name, user_name in transactions:
        if tx.type == TransactionType.expense:
            categories_summary[category_name] = categories_summary.get(category_name, 0) + tx.amount
        users_summary[user_name] = users_summary.get(user_name, 0) + tx.amount

    return {
        "start_date": req.start_date or (datetime.now() - timedelta(days=30)),
        "end_date": req.end_date or datetime.now(),
        "income_total": income_total,
        "expense_total": expense_total,
        "balance": income_total - expense_total,
        "categories_summary": categories_summary,
        "users_summary": users_summary,
        "transactions": [
            {
                "id": tx.id,
                "amount": tx.amount,
                "type": tx.type.value,
                "description": tx.description,
                "date": tx.date,
                "category": cat_name,
                "user": user_name
            }
            for tx, cat_name, user_name in transactions
        ],
    }


async def generate_report_pdf(db: AsyncSession, req: ReportRequest) -> str:
    """
    Генерирует PDF-файл отчёта и возвращает путь к нему.
    """

    data = await generate_report_data(db, req)

    template_dir = Path(__file__).parent.parent / "templates"
    template_dir.mkdir(exist_ok=True)

    # Создание шаблона, если его нет
    template_path = template_dir / "report_template.html"

    if not template_path.exists():
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Financial Report</title></head>
<body>
    <h1>Финансовый отчёт</h1>
    <p>Период: {{ start_date }} — {{ end_date }}</p>

    <h2>Итоги</h2>
    <ul>
        <li>Доходы: {{ income_total }}</li>
        <li>Расходы: {{ expense_total }}</li>
        <li>Баланс: {{ balance }}</li>
    </ul>

    <h2>Категории расходов</h2>
    <ul>
    {% for category, amount in categories_summary.items() %}
        <li>{{ category }}: {{ amount }}</li>
    {% endfor %}
    </ul>

    <h2>Пользователи</h2>
    <ul>
    {% for user, amount in users_summary.items() %}
        <li>{{ user }}: {{ amount }}</li>
    {% endfor %}
    </ul>

    <h2>Транзакции</h2>
    <table border="1" cellpadding="5">
        <tr><th>ID</th><th>Сумма</th><th>Тип</th><th>Описание</th><th>Дата</th><th>Категория</th><th>Пользователь</th></tr>
        {% for tx in transactions %}
        <tr>
            <td>{{ tx.id }}</td>
            <td>{{ tx.amount }}</td>
            <td>{{ tx.type }}</td>
            <td>{{ tx.description }}</td>
            <td>{{ tx.date }}</td>
            <td>{{ tx.category }}</td>
            <td>{{ tx.user }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
            """)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    html_content = template.render(**data)

    # Генерация PDF
    temp_dir = Path(tempfile.gettempdir()) / "financial_reports"
    temp_dir.mkdir(exist_ok=True)

    report_id = UUID(int=os.getpid()).hex  # можно использовать более надежный ID
    pdf_path = temp_dir / f"report_{report_id}.pdf"

    HTML(string=html_content).write_pdf(pdf_path)

    return str(pdf_path)


async def get_report_file_path(report_id: UUID) -> str:
    """
    Возвращает путь к файлу отчёта по его ID.
    """
    temp_dir = Path(tempfile.gettempdir()) / "financial_reports"
    pdf_path = temp_dir / f"report_{report_id}.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"Report file {report_id} not found.")
    return str(pdf_path)


async def log_report_generation(db: AsyncSession, user_id: UUID, req: ReportRequest) -> None:
    """
    Логирование факта генерации отчёта.
    Можно сохранять в таблицу `report_logs`.
    Пока просто заглушка.
    """
    # TODO: Реализовать логирование в БД
    pass