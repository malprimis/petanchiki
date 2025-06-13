import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, intpk, created_at, updated_at


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(sa.String(150))
    owner_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('users.id'))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user_groups: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        back_populates="group",
        cascade="all, delete-orphan",
        overlaps="members,groups,user_groups"
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_groups",
        back_populates="groups",
        overlaps="user_groups,group"
    )
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_groups"
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