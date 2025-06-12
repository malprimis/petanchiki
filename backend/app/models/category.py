from ..models import (
    intpk, created_at, Base, String, Group, Transaction,
    mapped_column, Mapped, UUID, ForeignKey, relationship
)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[intpk]
    group_id: Mapped[UUID] = mapped_column(ForeignKey('groups.id'))
    name: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[created_at]

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="categories",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
    )