from ..models import (
    intpk, created_at, updated_at, Base, String, UserGroup, User, Category, Transaction,
    mapped_column, Mapped, UUID, ForeignKey, relationship
)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(150))
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user_groups: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_groups",
        back_populates="groups",
    )

    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="group",
        cascade="all, delete-orphan",
    )