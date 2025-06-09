from ..models import (
    intpk, created_at, updated_at, Base, String,
    mapped_column, Mapped, Role
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
