from app.db.base import UserRole, GroupRole
from app.models.group import Group
from app.models.user import User
from app.models.user_group import UserGroup


def test_user_group_membership(db_session):
    user = User(
        email="member@example.com",
        name="Member",
        password_hash="h",
        role=UserRole.user
    )
    group = Group(name="Members Group", owner=user)
    db_session.add_all([user, group])
    db_session.flush()

    ug = UserGroup(user=user, group=group, role=GroupRole.member)
    db_session.add(ug)
    db_session.flush()

    # Проверяем связи association-object
    assert ug.user is user
    assert ug.group is group
    assert user.groups == [group]
    assert group.members == [user]
