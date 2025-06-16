import os






import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.report import ReportRequest
from app.services.user_service import get_user_by_id
from app.services.category_service import get_category_by_id

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


async def generate_report_data(
    db: AsyncSession,
    req: ReportRequest
) -> dict[str, Any]:
    """
    Возвращает словарь с ключами:
      - income_total: float
      - expense_total: float
      - by_category: dict[name, sum] (если req.by_category)
      - by_user: dict[name, sum]     (если req.by_user)
    """
    # 1) Считаем общий доход
    income_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(
            Transaction.group_id == req.group_id,
            Transaction.type == "income",
            *([Transaction.date >= req.date_from] if req.date_from else []),
            *([Transaction.date <= req.date_to]   if req.date_to   else []),
        )
    )
    total_income = income_res.scalar_one()

    # 2) Считаем общий расход
    expense_res = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(
            Transaction.group_id == req.group_id,
            Transaction.type == "expense",
            *([Transaction.date >= req.date_from] if req.date_from else []),
            *([Transaction.date <= req.date_to]   if req.date_to   else []),
        )
    )
    total_expense = expense_res.scalar_one()

    # 3) Разбивка по категориям
    by_cat: Optional[dict[str, float]] = None
    if req.by_category:
        stmt = (
            select(Transaction.category_id, func.coalesce(func.sum(Transaction.amount), 0.0))
            .where(
                Transaction.group_id == req.group_id,
                *([Transaction.date >= req.date_from] if req.date_from else []),
                *([Transaction.date <= req.date_to]   if req.date_to   else []),
            )
            .group_by(Transaction.category_id)
        )
        rows = await db.execute(stmt)
        by_cat = {}
        for cat_id, amt in rows.all():
            cat = await get_category_by_id(db, cat_id)
            if cat:
                by_cat[cat.name] = amt

    # 4) Разбивка по пользователям
    by_usr: Optional[dict[str, float]] = None
    if req.by_user:
        stmt = (
            select(Transaction.user_id, func.coalesce(func.sum(Transaction.amount), 0.0))
            .where(
                Transaction.group_id == req.group_id,
                *([Transaction.date >= req.date_from] if req.date_from else []),
                *([Transaction.date <= req.date_to]   if req.date_to   else []),
            )
            .group_by(Transaction.user_id)
        )
        rows = await db.execute(stmt)
        by_usr = {}
        for user_id, amt in rows.all():
            user = await get_user_by_id(db, user_id)
            if user:
                by_usr[user.name] = amt

    # Собираем итоговый словарь
    result: dict[str, Any] = {
        "income_total": total_income,
        "expense_total": total_expense,
    }
    if req.by_category:
        result["by_category"] = by_cat or {}
    if req.by_user:
        result["by_user"] = by_usr or {}
    return result


async def generate_report_pdf(
    db: AsyncSession,
    req: ReportRequest
) -> Path:
    """
    Генерирует PDF-файл через ReportLab и возвращает Path к нему.
    """
    data = await generate_report_data(db, req)

    # 1) Придумываем уникальное имя и готовим canvas
    report_id = uuid.uuid4()
    filename = f"report_{report_id}.pdf"
    filepath: Path = Path(REPORTS_DIR) / filename

    c = canvas.Canvas(str(filepath), pagesize=A4)
    width, height = A4

    # 2) Шапка
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, f"Report for Group {req.group_id}")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 2.5*cm, f"Period: {req.date_from or '–'} to {req.date_to or '–'}")
    c.drawString(2*cm, height - 3*cm, f"Generated: {datetime.utcnow().isoformat()} UTC")

    # 3) Контент
    y = height - 4*cm
    if data.get("by_category"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "By Category:")
        y -= 1*cm
        c.setFont("Helvetica", 10)
        for name, amt in data["by_category"].items():
            c.drawString(3*cm, y, f"{name}: {amt}")
            y -= 0.7*cm
        y -= 0.5*cm

    if data.get("by_user"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "By User:")
        y -= 1*cm
        c.setFont("Helvetica", 10)
        for name, amt in data["by_user"].items():
            c.drawString(3*cm, y, f"{name}: {amt}")
            y -= 0.7*cm
        y -= 0.5*cm

    # 4) Итоги
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, f"Total Expense: {data['expense_total']}")
    y -= 1*cm
    c.drawString(2*cm, y, f"Total Income : {data['income_total']}")

    c.showPage()
    c.save()

    return filepath


async def get_report_file_path(report_id: uuid.UUID) -> Path:
    """
    Ищет файл report_<report_id>.pdf в REPORTS_DIR и возвращает Path.
    """
    pattern = f"report_{report_id}"
    for fname in os.listdir(REPORTS_DIR):
        if fname.startswith(pattern):
            return Path(REPORTS_DIR) / fname
    raise FileNotFoundError(f"Report {report_id} not found")
