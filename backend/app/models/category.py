import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, intpk, created_at


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[intpk]
    group_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('groups.id'))
    name: Mapped[str] = mapped_column(sa.String(100))
    icon: Mapped[str | None] = mapped_column(sa.String(100))
    created_at: Mapped[created_at]

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="categories",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
    )