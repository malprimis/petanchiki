import math
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import TransactionType
from app.models.transaction import Transaction
from app.schemas.report import ReportPdfRequest
from app.services.category_service import get_category_by_id
from app.services.user_service import get_user_by_id

# Регистрация шрифта для кириллицы
FONT_PATH = Path(__file__).parent.parent / "static" / "fonts" / "DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONT_PATH)))

# Директория для отчетов
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Цветовая палитра (Tableau10)
PALETTE = [colors.HexColor(h) for h in [
    "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
    "#59a14f", "#edc949", "#af7aa1", "#ff9da7",
    "#9c755f", "#bab0ab",
]]
# Цвет для "Прочие"
GREY_OTHER = colors.HexColor("#666666")

async def generate_report_data(
    db: AsyncSession,
    req: ReportPdfRequest
) -> Dict[str, Any]:
    """
    Формирует агрегированные данные по доходам и расходам для отчёта.

    :param db: асинхронная сессия SQLAlchemy
    :param req: параметры запроса для отчёта (группа, даты)
    :return: словарь с агрегированными значениями по категориям и пользователям
    """
    filters = []
    if req.date_from:
        filters.append(Transaction.date >= req.date_from)
    if req.date_to:
        filters.append(Transaction.date <= req.date_to)

    stmt_sum = lambda ttype: select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
        Transaction.group_id == req.group_id,
        Transaction.type == ttype,
        *filters
    )
    total_income = (await db.execute(stmt_sum(TransactionType.income))).scalar_one()
    total_expense = (await db.execute(stmt_sum(TransactionType.expense))).scalar_one()

    async def aggregate(stmt, fetch):
        out = {}
        for key, amt in (await db.execute(stmt)).all():
            entity = await fetch(db, key)
            out[entity.name] = float(amt)
        return out

    build_stmt = lambda attr, ttype: select(attr, func.coalesce(func.sum(Transaction.amount), 0.0)).where(
        Transaction.group_id == req.group_id,
        Transaction.type == ttype,
        *filters
    ).group_by(attr)

    inc_cat = build_stmt(Transaction.category_id, TransactionType.income)
    exp_cat = build_stmt(Transaction.category_id, TransactionType.expense)
    inc_usr = build_stmt(Transaction.user_id, TransactionType.income)
    exp_usr = build_stmt(Transaction.user_id, TransactionType.expense)

    return {
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "by_category_income": await aggregate(inc_cat, get_category_by_id),
        "by_category_expense": await aggregate(exp_cat, get_category_by_id),
        "by_user_income": await aggregate(inc_usr, get_user_by_id),
        "by_user_expense": await aggregate(exp_usr, get_user_by_id),
    }

async def generate_report_pdf(
    db: AsyncSession,
    req: ReportPdfRequest
) -> Path:
    """
    Генерирует PDF-отчёт по транзакциям группы с графиками и таблицей.

    :param db: асинхронная сессия SQLAlchemy
    :param req: параметры отчёта (группа, диапазон дат)
    :return: путь к сгенерированному PDF-файлу
    """
    data = await generate_report_data(db, req)
    report_id = uuid.uuid4()
    output_path = REPORTS_DIR / f"report_{report_id}.pdf"
    c = Canvas(str(output_path), pagesize=A4)
    w, h = A4

    # Заголовок
    c.setFont("DejaVuSans", 16)
    c.drawString(2*cm, h-2*cm, f"Отчёт по группе {req.group_id}")
    c.setFont("DejaVuSans", 10)
    period = f"{req.date_from or '-'} — {req.date_to or '-'}"
    c.drawString(2*cm, h-2.5*cm, f"Период: {period}")
    c.drawString(2*cm, h-3*cm, f"Сгенерировано: {datetime.now().isoformat()} UTC")

    margin = 2*cm
    chart_size = 4*cm
    y = h - 4*cm

    def draw_section(title:str, items:Dict[str,float], y0:float)->float:
        # группировка
        N=5
        si = sorted(items.items(),key=lambda kv:kv[1],reverse=True)
        grp = si[:N] + [("Прочие",sum(v for _,v in si[N:]))] if len(si)>N else si

        y1 = y0 - cm
        if not grp:
            return y1
        # заголовок
        c.setFont('DejaVuSans',12)
        c.setFillColor(colors.black)

        c.drawString(margin,y0,title)
        # отступ всегда

        labels, vals = zip(*grp)
        tot = sum(vals) or 1.0
        pad, box = 0.5*cm,0.4*cm

        # легенда
        lx, ly = margin, y1
        c.setFont('DejaVuSans',10)
        for i,(lbl,val) in enumerate(grp):
            col = GREY_OTHER if lbl=='Прочие' else PALETTE[i%len(PALETTE)]
            c.setFillColor(col);c.rect(lx,ly-box,box,box,fill=1,stroke=0)
            c.setFillColor(colors.black)
            c.drawString(lx+box+0.2*cm,ly-box+2,f"{lbl} ({val:.2f})")
            ly -= box+0.3*cm

        # круг
        cx,cy = w-margin-chart_size/2, y1-pad-chart_size/2
        r = chart_size/2
        c.setLineWidth(1);c.setStrokeColor(colors.black)
        start=0
        for i,(lbl,val) in enumerate(grp):
            ang = val/tot*360
            col = GREY_OTHER if lbl=='Прочие' else PALETTE[i%len(PALETTE)]
            c.setFillColor(col);c.wedge(cx-r,cy-r,cx+r,cy+r,start,ang,fill=1,stroke=1)
            mid = start+ang/2;rad=math.radians(mid)
            tx,ty = cx+0.6*r*math.cos(rad), cy+0.6*r*math.sin(rad)
            txtcol = colors.white
            c.setFillColor(txtcol);c.setFont('DejaVuSans',10)
            c.drawCentredString(tx,ty,f"{val/tot*100:.0f}%")
            start+=ang
        c.circle(cx,cy,r,stroke=1,fill=0)

        used = max(len(grp)*(box+0.3*cm),chart_size)
        return y1 - used - cm

    # Отрисовка секций
    y = draw_section("Траты по категориям:", data["by_category_expense"], y)
    y = draw_section("Доходы по категориям:", data["by_category_income"], y)
    y = draw_section("Траты по пользователям:", data["by_user_expense"], y)
    y = draw_section("Доходы по пользователям:", data["by_user_income"], y)

    # Итоги
    c.setFont("DejaVuSans", 12)
    c.setFillColor(colors.black)
    c.drawString(margin, y, f"Всего расходов: {data['total_expense']:.2f}")
    c.drawString(margin, y-cm, f"Всего доходов: {data['total_income']:.2f}")

    # Таблица транзакций
    c.showPage()
    c.setFont("DejaVuSans", 12)
    c.drawString(margin, h-2*cm, "Список транзакций:")

    # Сбор транзакций
    filters = []
    if req.date_from:
        filters.append(Transaction.date >= req.date_from)
    if req.date_to:
        filters.append(Transaction.date <= req.date_to)
    stmt = select(Transaction).where(Transaction.group_id == req.group_id, *filters).order_by(Transaction.date)
    txs = (await db.execute(stmt)).scalars().all()

    # Подготовка данных таблицы
    table_data = [["Дата", "Тип", "Категория", "Пользователь", "Описание", "Сумма"]]
    for tx in txs:
        cat = await get_category_by_id(db, tx.category_id)
        user = await get_user_by_id(db, tx.user_id)

        type_rus = "Доходы" if tx.type == TransactionType.income else "Расходы"
        table_data.append([
            tx.date.strftime('%Y-%m-%d'),
            type_rus,
            cat.name,
            user.name,
            tx.description or "",
            f"{tx.amount:.2f}"
        ])

    # Создание и отрисовка таблицы
    col_widths = [2.5*cm, 2*cm, 3*cm, 3*cm, 5*cm, 2.5*cm]
    tbl = Table(table_data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    # Вычисление высоты таблицы
    row_height = 0.7 * cm
    table_height = row_height * len(table_data)
    y_table_start = h - 3 * cm
    tbl.wrapOn(c, w - 2 * margin, table_height)
    tbl.drawOn(c, margin, y_table_start - table_height)

    c.save()
    return output_path





async def get_report_file_path(report_id: uuid.UUID) -> Path:
    """
    Возвращает путь к сохранённому PDF-отчёту по report_id.

    :param report_id: UUID отчёта
    :return: путь к PDF-файлу
    :raises FileNotFoundError: если файл не найден
    """
    pattern = f"report_{report_id}"
    for file in REPORTS_DIR.iterdir():
        if file.name.startswith(pattern) and file.suffix == ".pdf":
            return file
    raise FileNotFoundError(f"Report {report_id} not found")
