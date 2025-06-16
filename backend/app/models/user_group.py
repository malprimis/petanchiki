import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, intpk, created_at, GroupRole


class UserGroup(Base):
    __tablename__ = 'user_groups'

    id: Mapped[intpk]
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('users.id'))
    group_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('groups.id'))
    role: Mapped[GroupRole] = mapped_column(default=GroupRole.member, server_default=GroupRole.member.value)
    joined_at: Mapped[created_at]

    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_groups",
        overlaps="members,groups,user_groups"
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="user_groups",
        overlaps="members,groups"
    )