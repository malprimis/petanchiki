import datetime

from ..models import (
    intpk, created_at, updated_at, Base, Numeric, relationship, Group, Category, User,
    mapped_column, Mapped, UUID, ForeignKey, TransactionType
)



class Transaction(Base):
    __tablename__ = 'transactions'

    id:  Mapped[intpk]
    group_id: Mapped[UUID] = mapped_column(ForeignKey('groups.id'))
    category_id: Mapped[UUID] = mapped_column(ForeignKey('categories.id'))
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    amount: Mapped[float] = mapped_column(Numeric(precision=12, scale=2))
    type: Mapped[TransactionType]
    description: Mapped[str | float]
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
