import uuid

from app.db.base import UserRole
from app.models.group import Group
from app.models.user import User


def test_group_owner_relationship(db_session):
    # Создаём пользователя
    user = User(
        email="owner@example.com",
        name="Owner",
        password_hash="h",
        role=UserRole.admin
    )
    db_session.add(user)
    db_session.flush()
    assert isinstance(user.id, uuid.UUID)

    # Создаём группу, указывая owner через relationship
    group = Group(name="Test Group", owner=user)
    db_session.add(group)
    db_session.flush()

    # Проверяем, что FK и relationship работают
    assert group.owner is user
    assert group.owner_id == user.id
    assert group in user.owned_groups
