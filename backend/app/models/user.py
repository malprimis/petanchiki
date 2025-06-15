import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, intpk, created_at, updated_at, UserRole


class User(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(sa.String(255), unique=True)
    name: Mapped[str] = mapped_column(sa.String(30))
    password_hash: Mapped[str] = mapped_column(sa.String(255))
    role: Mapped[UserRole] = mapped_column(default=UserRole.user, server_default=UserRole.user.value)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.text('true'))
    deleted_at: Mapped[datetime.datetime | None]

    user_groups: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="groups,group,user_groups"
    )
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="user_groups",
        back_populates="members",
        overlaps="user_groups,user"
    )
    owned_groups: Mapped[list["Group"]] = relationship(
        "Group",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def is_admin(self):
        return self.role == UserRole.admin