
from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.base import TransactionType
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.services.category_service import get_category_by_id
from app.services.group_service import is_user_member_in_group
from app.services.transaction_service import (
    create_transaction as svc_create,
    get_transaction_by_id as svc_get,
    list_transactions as svc_list,
    update_transaction as svc_update,
    delete_transaction as svc_delete,
    check_transaction_permission,
)

router = APIRouter(
    tags=["Transactions"]
)


@router.post(
    '/transactions',
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary='Create transaction'
)
async def create_transaction_endpoint(
        payload: TransactionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(get_current_active_user)
):
    if not await is_user_member_in_group(db, payload.group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a group member")

    category = await get_category_by_id(db, payload.category_id)
    if not category or category.group_id != payload.group_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category does not belong to specified group")

    return await svc_create(db, payload, current_user.id)



@router.get(
    "/transactions",
    response_model=List[TransactionRead],
    summary="List transactions in a group",
)
async def list_transactions_endpoint(
    group_id: UUID = Query(..., description="UUID of the group"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: UUID | None = Query(None, description="Filter by author UUID"),
    category_id: UUID | None = Query(None, description="Filter by category UUID"),
    date_from: date | None = Query(None),
    date_to:   date | None = Query(None),
    tx_type:   TransactionType | None  = Query(None, description="'income' or 'expense'"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    if not await is_user_member_in_group(db, group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a group member")

    return await svc_list(
        db,
        group_id=group_id,
        skip=skip,
        limit=limit,
        user_id=user_id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        tx_type=tx_type,
    )


@router.get(
    "/transactions/{tx_id}",
    response_model=TransactionRead,
    summary="Get a transaction by ID",
)
async def get_transaction_endpoint(
    tx_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    tx = await svc_get(db, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    allowed = await check_transaction_permission(db, tx, current_user.id)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")
    return tx


@router.patch(
    "/transactions/{tx_id}",
    response_model=TransactionRead,
    summary="Update a transaction",
)
async def update_transaction_endpoint(
    tx_id: UUID,
    payload: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    tx = await svc_get(db, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    updated = await svc_update(db, tx, payload, current_user.id)
    return updated


@router.delete(
    "/transactions/{tx_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
)
async def delete_transaction_endpoint(
    tx_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """
    Удаляет транзакцию (hard delete).
    Разрешено автору или админам группы.
    """
    tx = await svc_get(db, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    await svc_delete(db, tx, current_user.id)
    return None