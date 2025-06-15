import uuid
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def is_category_name_unique(
        db: AsyncSession,
        group_id: uuid.UUID,
        name: str
) -> bool:

    stmt = (
        select(Category)
        .filter(Category.group_id == group_id,
                Category.name == name)
    )

    result = await db.execute(stmt)
    return result.scalars().first() is None


async def create_category(
        db: AsyncSession,
        cat_in: CategoryCreate,
        group_id: uuid.UUID
) -> Category:

    check_unique = await is_category_name_unique(db, group_id, cat_in.name)
    if not check_unique:
        raise HTTPException(status_code=400, detail='Category name must be unique within the group')

    category = Category(
        group_id=group_id,
        name=cat_in.name,
        icon=cat_in.icon
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


async def get_category_by_id(
        db: AsyncSession,
        category_id: uuid.UUID
) -> Category:

    stmt = (
        select(Category)
        .filter(Category.id == category_id)
    )

    result = await db.execute(stmt)
    return result.scalars().first()


async def list_categories_for_group(
        db: AsyncSession,
        group_id: uuid.UUID
) -> Sequence[Category]:

    stmt = (
        select(Category)
        .filter(Category.group_id == group_id)
    )

    result = await db.execute(stmt)

    return result.scalars().all()


async def update_category(
        db: AsyncSession,
        category: Category,
        cat_in: CategoryUpdate
) -> Category:

    updated = False

    if cat_in.name is not None and cat_in.name != category.name:

        if not await is_category_name_unique(db, category.group_id, cat_in.name):
            raise HTTPException(status_code=400, detail='Category name must be unique within the group')

        category.name = cat_in.name
        updated = True

    if cat_in.icon is not None:
        category.icon = cat_in.icon
        updated = True


    if updated:
        await db.commit()
        await db.refresh(category)

    return category


async def delete_category(
        db: AsyncSession,
        category: Category
) -> None:

    await db.delete(category)
    await db.commit()