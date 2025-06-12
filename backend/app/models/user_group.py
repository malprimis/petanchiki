from ..models import (
    intpk, created_at, Base, GroupRole, User, Group,
    mapped_column, Mapped, UUID, ForeignKey, relationship
)


class UserGroup(Base):
    __tablename__ = 'user_groups'

    id: Mapped[intpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
    group_id: Mapped[UUID] = mapped_column(ForeignKey('groups.id'))
    role: Mapped[GroupRole]
    joined_at: Mapped[created_at]

    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_groups",
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="user_groups",
    )