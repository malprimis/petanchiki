import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import TransactionType
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user_group import UserGroup
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.group_service import is_user_admin_in_group


async def create_transaction(
        db: AsyncSession,
        tx_in: TransactionCreate,
        author_id: uuid.UUID
) -> Transaction:
    membership = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == tx_in.group_id,
                UserGroup.user_id == author_id)
    )

    if not membership.scalars().first():
        raise HTTPException(status_code=403, detail='User not in group')

    category = await db.execute(
        select(Category)
        .filter(Category.group_id == tx_in.group_id,
                Category.id == tx_in.category_id)
    )

    if not category.scalars().first():
        raise HTTPException(status_code=400, detail='Category not in group')

    tx = Transaction(
        group_id=tx_in.group_id,
        category_id=tx_in.category_id,
        user_id=author_id,
        amount=tx_in.amount,
        type=tx_in.type,
        description=tx_in.description,
        date=tx_in.date
    )

    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


async def get_transaction_by_id(
        db: AsyncSession,
        tx_id: uuid.UUID
) -> Transaction:

    result = await db.execute(
        select(Transaction)
        .filter(Transaction.id == tx_id)
    )

    return result.scalars().first()


async def list_transactions(
        db: AsyncSession,
        group_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        user_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        tx_type: TransactionType | None = None
) -> Sequence[Transaction]:

    stmt = select(Transaction).filter(Transaction.group_id == group_id)

    if user_id:
        stmt = stmt.filter(Transaction.user_id == user_id)
    if category_id:
        stmt = stmt.filter(Transaction.category_id == category_id)
    if date_from:
        stmt = stmt.filter(Transaction.date >= date_from)
    if date_to:
        stmt = stmt.filter(Transaction.date <= date_to)
    if tx_type:
        stmt = stmt.filter(Transaction.type == tx_type)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def check_transaction_permission(
        db: AsyncSession,
        tx: Transaction,
        user_id: uuid.UUID
) -> bool:

    if tx.user_id == user_id:
        return True

    return await is_user_admin_in_group(db, tx.group_id, user_id)


async def update_transaction(
        db: AsyncSession,
        tx: Transaction,
        tx_in: TransactionUpdate,
        current_user_id: uuid.UUID
) -> Transaction:
    if not await check_transaction_permission(db, tx, current_user_id):
        raise HTTPException(status_code=403, detail='forbidden')

    updated = False

    if tx_in.amount is not None:
        tx.amount = tx_in.amount
        updated = True
    if tx_in.description is not None:
        tx.description = tx_in.description
        updated = True
    if tx_in.type is not None:
        tx.type = tx_in.type
        updated = True
    if tx_in.date is not None:
        tx.date = tx_in.date
        updated = True
    if tx_in.category_id is not None:
        cat = await db.execute(
            select(Category)
            .filter(Category.id == tx_in.category_id,
                    Category.group_id == tx.group_id)
        )

        if not cat.scalars().first():
            raise HTTPException(status_code=400, detail='Invalid category for this group')

        tx.category_id = tx_in.category_id
        updated = True

    if updated:
        await db.commit()
        await db.refresh(tx)

    return tx


async def delete_transaction(
        db: AsyncSession,
        tx: Transaction,
        current_user_id: uuid.UUID
) -> None:

    check_permission = await check_transaction_permission(db, tx, current_user_id)

    if not check_permission:
        raise HTTPException(status_code=403, detail='forbidden')

    await db.execute(
        delete(Transaction)
        .filter(Transaction.id == tx.id)
    )
    await db.commit()
