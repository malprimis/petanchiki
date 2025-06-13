import datetime
import enum
import uuid
from typing import Annotated

from sqlalchemy import func, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import UUID

intpk = Annotated[UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
intpkdef = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )
]

updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
]

class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f'{col} = {getattr(self, col)}')

        return f'<{self.__class__.__name__}: {', '.join(cols)}>'


class UserRole(enum.Enum):
    admin = 'admin'
    user = 'user'


class GroupRole(enum.Enum):
    admin  = "admin"
    member = "member"


class TransactionType(enum.Enum):
    expense = 'expense'
    income = 'income'
