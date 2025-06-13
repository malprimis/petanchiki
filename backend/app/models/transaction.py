import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, intpk, created_at, updated_at, TransactionType


class Transaction(Base):
    __tablename__ = 'transactions'

    id:  Mapped[intpk]
    group_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('groups.id'))
    category_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('categories.id'))
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('users.id'))
    amount: Mapped[float] = mapped_column(sa.Numeric(precision=12, scale=2))
    type: Mapped[TransactionType]
    description: Mapped[str | None]
    date: Mapped[datetime.datetime]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="transactions",
    )
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="transactions",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
    )
