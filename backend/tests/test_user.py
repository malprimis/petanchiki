import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.base import UserRole
from app.models.user import User


def test_user_creation(db_session):
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash="hash",
        role=UserRole.user
    )
    db_session.add(user)
    db_session.flush()

    assert isinstance(user.id, uuid.UUID)
    assert user.created_at is not None
    assert user.updated_at is not None

def test_unique_email(db_session):
    u1 = User(
        email="dup@example.com",
        name="A",
        password_hash="h",
        role=UserRole.user
    )
    db_session.add(u1)
    db_session.flush()

    u2 = User(
        email="dup@example.com",
        name="B",
        password_hash="h2",
        role=UserRole.user
    )
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.flush()
