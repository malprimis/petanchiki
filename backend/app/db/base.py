import enum
import uuid
import datetime
from typing import Annotated
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import UUID

intpk = Annotated[UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
intpkdef = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                        onupdate=datetime.datetime.now)]


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f'{col} = {getattr(self, col)}')

        return f'<{self.__class__.__name__}: {', '.join(cols)}>'


class Role(enum.Enum):
    admin = 'admin'
    user = 'user'
