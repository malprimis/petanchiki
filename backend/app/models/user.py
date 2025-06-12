from ..models import (
    intpk, created_at, updated_at, Base, String, Transaction,
    mapped_column, Mapped, UserRole, UserGroup, Group, relationship
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user_groups: Mapped[list["UserGroup"]] = relationship(
        "UserGroup",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="user_groups",
        back_populates="members",
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )