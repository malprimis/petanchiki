from ..models import (
    intpk, created_at, updated_at, Base, String,
    mapped_column, Mapped, Role, UUID, ForeignKey
)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(150))
    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]