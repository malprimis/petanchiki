# app/services/report_service.py
import os
import uuid
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.utils import ImageReader
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category  # Добавлено: тебе нужна модель категории
from app.schemas.report import ReportRequest
from app.services.user_service import get_user_by_id
from app.services.category_service import get_category_by_id

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Убедись, что директория существует
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


async def generate_report_data(
    db: AsyncSession,
    req: ReportRequest
) -> dict[str, Any]:
    """
    Генерирует агрегированные данные отчёта по группе.
    """

    # --- Доходы ---
    income_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(
            Transaction.group_id == req.group_id,
            Transaction.type == "income",
            *([Transaction.date >= req.date_from] if req.date_from else []),
            *([Transaction.date <= req.date_to] if req.date_to else []),
        )
    )
    total_income = income_res.scalar_one()

    # --- Расходы ---
    expense_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(
            Transaction.group_id == req.group_id,
            Transaction.type == "expense",
            *([Transaction.date >= req.date_from] if req.date_from else []),
            *([Transaction.date <= req.date_to] if req.date_to else []),
        )
    )
    total_expense = expense_res.scalar_one()
    balance = total_income - total_expense

    # --- Транзакции ---
    stmt = (
        select(Transaction)
        .where(
            Transaction.group_id == req.group_id,
            *([Transaction.date >= req.date_from] if req.date_from else []),
            *([Transaction.date <= req.date_to] if req.date_to else []),
        )
    )
    result = await db.execute(stmt)
    transactions = result.scalars().all()

    # --- Разбивка по категориям ---
    by_category: Optional[Dict[str, float]] = None
    if req.by_category:
        cat_stmt = (
            select(Transaction.category_id, func.sum(Transaction.amount).cast(func.Numeric(10, 2)))
            .where(
                Transaction.group_id == req.group_id,
                *([Transaction.date >= req.date_from] if req.date_from else []),
                *([Transaction.date <= req.date_to] if req.date_to else []),
            )
            .group_by(Transaction.category_id)
        )
        cat_result = await db.execute(cat_stmt)
        categories = cat_result.all()
        by_category = {}
        for cat_id, amt in categories:
            category = await get_category_by_id(db, cat_id)
            if category:
                by_category[category.name] = float(amt)

    # --- Разбивка по пользователям ---
    by_user: Optional[Dict[str, float]] = None
    if req.by_user:
        user_stmt = (
            select(Transaction.user_id, func.sum(Transaction.amount).cast(func.Numeric(10, 2)))
            .where(
                Transaction.group_id == req.group_id,
                *([Transaction.date >= req.date_from] if req.date_from else []),
                *([Transaction.date <= req.date_to] if req.date_to else []),
            )
            .group_by(Transaction.user_id)
        )
        user_result = await db.execute(user_stmt)
        users = user_result.all()
        by_user = {}
        for user_id, amt in users:
            user = await get_user_by_id(db, user_id)
            if user:
                by_user[user.name] = float(amt)

    return {
        "income_total": float(total_income),
        "expense_total": float(total_expense),
        "balance": float(balance),
        "transactions": [
            {
                "id": str(tx.id),
                "amount": float(tx.amount),
                "type": tx.type.value,
                "description": tx.description or "",
                "date": tx.date.isoformat() if tx.date else "",
                "user_id": str(tx.user_id),
                "category_id": str(tx.category_id),
            }
            for tx in transactions
        ],
        "by_category": by_category or {},
        "by_user": by_user or {},
    }


from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Путь к шрифту с поддержкой кириллицы
FONT_PATH = Path("static/fonts/DejaVuSans.ttf")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def generate_category_pie_chart(data: dict) -> ImageReader:
    """
    Создаёт круговую диаграмму расходов по категориям и возвращает как ImageReader.
    """
    if not data:
        raise ValueError("Нет данных для построения диаграммы")

    labels = list(data.keys())
    sizes = list(data.values())

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontname': 'DejaVu Sans', 'fontsize': 10}
    )
    ax.axis('equal')  # Для круглой формы диаграммы
    plt.title("Распределение расходов по категориям")

    # Сохраняем изображение в буфер
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    plt.close()

    # Возвращаем как ImageReader для ReportLab
    return ImageReader(BytesIO(img_data.getvalue()))

async def generate_report_pdf(
    db: AsyncSession,
    req: ReportRequest
) -> Path:
    data = await generate_report_data(db, req)

    # Создаём файл
    report_id = uuid.uuid4()
    filename = f"report_{report_id}.pdf"
    filepath = REPORTS_DIR / filename

    # --- Настройка холста ---
    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4

    # --- Регистрация шрифта с поддержкой кириллицы ---
    if FONT_PATH.exists():
        pdfmetrics.registerFont(TTFont('DejaVu', str(FONT_PATH)))
        c.setFont("DejaVu", 10)
    else:
        c.setFont("Helvetica", 10)

    # --- Логотип ---
    logo_path = Path("static") / "logo.png"
    if logo_path.exists():
        c.drawImage(str(logo_path), x=2 * cm, y=height - 3 * cm, width=2.5 * cm, height=1.5 * cm)

    # --- Заголовок ---
    y = height - 5 * cm  # Смещаем ниже для логотипа

    if FONT_PATH.exists():
        c.setFont("DejaVu", 16)
    else:
        c.setFont("Helvetica-Bold", 16)

    c.drawString(5.5 * cm, y, f"Финансовый отчёт — группа {req.group_id}")
    y -= 0.7 * cm
    c.setFont("DejaVu", 10) if FONT_PATH.exists() else c.setFont("Helvetica", 10)
    c.drawString(5.5 * cm, y, f"Период: {req.date_from or 'начала'} — {req.date_to or 'сегодня'}")
    y -= 0.5 * cm
    c.drawString(5.5 * cm, y, f"Сгенерировано: {datetime.now().isoformat()}")
    y -= 1.5 * cm

    # --- Таблица Итогов ---
    summary_data = [
        ["Income", "Expense", "Balance"],
        [data['income_total'], data['expense_total'], data['balance']]
    ]
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    summary_table.wrapOn(c, width, height)
    summary_table.drawOn(c, 2 * cm, y)
    y -= 2 * cm

    # Рисуем диаграмму
    if data["by_category"]:
        img_reader = generate_category_pie_chart(data["by_category"])
        c.drawImage(img_reader, 2 * cm, y - 8 * cm, width=12 * cm, height=8 * cm)
        y -= 9 * cm

    # --- Таблица по категориям ---
    if data["by_category"]:
        category_data = [["Category", "Amount"]]
        for name, amount in data["by_category"].items():
            category_data.append([name, amount])

        category_table = Table(category_data)
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        category_table.wrapOn(c, width, height)
        category_table.drawOn(c, 2 * cm, y)
        y -= len(category_data) * 0.5 * cm + 0.5 * cm

    # --- Таблица по пользователям ---
    if data["by_user"]:
        user_data = [["User", "Amount"]]
        for name, amount in data["by_user"].items():
            user_data.append([name, amount])

        user_table = Table(user_data)
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        user_table.wrapOn(c, width, height)
        user_table.drawOn(c, 2 * cm, y)
        y -= len(user_data) * 0.5 * cm + 0.5 * cm

    # --- Таблица транзакций ---
    transaction_data = [["Data", "Type", "Description", "Amount"]]
    for tx in data["transactions"]:
        transaction_data.append([
            tx["date"],
            tx["type"],
            tx["description"] or "",
            tx["amount"]
        ])

    tx_table = Table(transaction_data, colWidths=[5 * cm, 2.5 * cm, 7 * cm, 3 * cm])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Если места не хватает — новая страница
    if y < len(transaction_data) * 0.5 * cm + 2 * cm:
        c.showPage()
        y = height - 3 * cm

    tx_table.wrapOn(c, width, height)
    tx_table.drawOn(c, 2 * cm, y)

    # --- Сохраняем PDF ---
    c.save()
    return filepath

async def get_report_file_path(report_id: uuid.UUID) -> Path:
    """
    Возвращает путь к файлу отчёта по его ID.
    """
    pattern = f"report_{report_id}"
    for fname in os.listdir(REPORTS_DIR):
        if fname.startswith(pattern):
            return REPORTS_DIR / fname
    raise FileNotFoundError(f"Report with ID {report_id} not found.")