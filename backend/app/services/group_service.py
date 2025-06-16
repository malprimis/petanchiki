import uuid
from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import GroupRole
from app.models.group import Group
from app.models.user import User
from app.models.user_group import UserGroup
from app.schemas.group import GroupCreate, GroupUpdate


async def create_group(
        db: AsyncSession,
        group_in: GroupCreate,
        owner_id: uuid.UUID
) -> Group:
    """Create a new *active* group and register its owner as **admin**.

    The helper performs two separate inserts within the same session:

    1. A new `~app.models.group.Group` is created using the user‑supplied
       *name* and *description*.
    2. A matching `~app.models.user_group.UserGroup` row that grants
       creating user an **admin** role inside the freshly created group.

    Persistence is done eagerly (two commits) to ensure the ``group.id`` is
    available for the *membership* record and that concurrent requests cannot
    observe a partially initialized group.

    Parameters
    ----------
    db:
        An **open** async SQLAlchemy session bound to the function caller's
        transaction context.
    group_in:
        Pydantic schema carrying the *name* and *description* fields provided by
        the client.
    owner_id:
        Primary‑key value of the user that initiates group creation.

    Returns
    -------
    Group
        A fully reflected ORM instance representing the persisted group,
        including an auto‑generated ``id``.

    Raises
    ------
    sqlalchemy.exc.SQLAlchemyError
        If the underlying insert statements fail (propagated unchanged).
    """
    group = Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=owner_id,
        is_active=True,
        deleted_at=None
    )

    db.add(group)
    await db.commit()

    group = await get_group_by_id(db, group.id)

    membership = UserGroup(
        group_id=group.id,
        user_id=owner_id,
        role=GroupRole.admin,
        joined_at=datetime.now()
    )
    db.add(membership)
    await db.commit()
    return group


async def get_group_by_id(
        db: AsyncSession,
        group_id: uuid.UUID,
        only_active: bool = True
) -> Group | None:
    """Retrieve a single group by its primary key.

    Parameters
    ----------
    db:
        Active SQLAlchemy async session.
    group_id:
        Primary key of the group to fetch.
    only_active:
        If *True* (default) the query filters out groups whose ``is_active`` flag
        is **False**. Toggle to *False* for administrative tooling that must
        inspect soft‑deleted groups.

    Returns
    -------
    Group | None
        The matching ORM instance **or** *None* when no such group exists (or is
        inactive when *only_active=True*).
    """
    stmt = select(Group).options(selectinload(Group.members))
    if only_active:
        stmt = stmt.filter(Group.is_active == True)  # noqa: E712
    stmt = stmt.filter(Group.id == group_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_group_by_user(
        db: AsyncSession,
        user_id: uuid.UUID
) -> Sequence[Group]:
    """Return all **active** groups the user participates in.

    Joins through the association table ``user_groups`` and returns each
    `Group` where a corresponding `UserGroup` entry exists for the
    supplied ``user_id``.

    Parameters
    ----------
    db:
        Async SQLAlchemy session.
    user_id:
        User identifier whose memberships must be listed.

    Returns
    -------
    Sequence[Group]
        A possibly empty *list‑like* collection containing the groups ordered in
        the order supplied by the database (usually primary‑key order).
    """
    stmt = (
        select(Group)
        .join(UserGroup, UserGroup.group_id == Group.id)
        .filter(UserGroup.user_id == user_id, Group.is_active == True)
        .options(selectinload(Group.members))
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def update_group(
        db: AsyncSession,
        group: Group,
        group_in: GroupUpdate,
        current_user: User
) -> Group:
    """Modify mutable attributes (``name``, ``description``) of a group.

    The operation is gated by *role‑based* access control:

    * **Admins** of the *same* group are allowed to update.
    * All other users receive *403 Forbidden* via `fastapi.HTTPException`.

    Parameters
    ----------
    db:
        Async session in the current request context.
    group:
        ORM instance representing the *target* group. Must already be attached
        to db.
    group_in:
        A *partial* instance whose attributes (``name``, ``description``) carry
        the new values. Attributes set to ``None`` are ignored.
    current_user:
        Authenticated user issuing the update.

    Returns
    -------
    Group
        The refreshed ORM instance after successful commit. If no fields were
        modified, the original object is returned unchanged.

    Raises
    ------
    fastapi.HTTPException
        * 403 – When the caller is **not** an admin of the group.
    """
    membership = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group.id, UserGroup.user_id == current_user.id)
    )
    mem = membership.scalars().first()
    if not mem or mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail="forbidden")

    updated = False

    if group_in.name is not None:
        group.name = group_in.name
        updated = True

    if group_in.description is not None:
        group.description = group_in.description
        updated = True

    if updated:
        await db.commit()
        await db.refresh(group)

    return group


async def delete_group(
        db: AsyncSession,
        group: Group,
        current_user: User
) -> None:
    """Soft‑delete a group.

    The operation **deactivates** the group (sets ``is_active=False``) and stores
    a timestamp in ``deleted_at``. Hard deletion is intentionally avoided to
    retain historical data for audit and reporting.

    Authorization
    -------------
    * **Group owner** – always allowed.
    * **Platform super‑admin** – allowed when ``current_user.is_admin`` is
      *True*.

    Parameters
    ----------
    db:
        Async SQLAlchemy session.
    group:
        ORM instance to be softly‑deleted.
    current_user:
        User attempting the deletion.

    Raises
    ------
    fastapi.HTTPException
        * 403 – When the caller lacks sufficient privileges.
    """
    if group.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="forbidden")

    group.is_active = False
    group.deleted_at = datetime.now()
    await db.commit()


async def add_user_to_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        role: GroupRole = GroupRole.member
) -> UserGroup:
    """Invite a user to a group or promote them directly to a given *role*.

    Two validation steps are performed before insertion:

    1. The *group* must exist and be active.
    2. The *user* must exist and be active.

    If the *membership* row already exists, an HTTP 400 is returned so that
    idempotent clients can detect a duplicate invitation.

    Parameters
    ----------
    db:
        Async SQLAlchemy session.
    group_id:
        Identifier of the target group.
    user_id:
        Identifier of the user to invite.
    role:
        Initial `~app.db.base.GroupRole` value. Defaults to `GroupRole.member`.

    Returns
    -------
    UserGroup
        The freshly persisted membership object.

    Raises
    ------
    fastapi.HTTPException
        * 404 – Group **or** user does not exist / is inactive.
        * 400 – Membership already present.
    """
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    user_stmt = await db.execute(
        select(User).filter(User.id == user_id, User.is_active == True)  # noqa: E712
    )
    user = user_stmt.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    exists_stmt = await db.execute(
        select(UserGroup).filter(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
    )
    exists = exists_stmt.scalars().first()

    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    membership = UserGroup(
        group_id=group_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now()
    )

    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def remove_user_from_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        current_user: User
) -> None:
    """Kick a member out of a group.

    Only *group admins* are authorized to perform the removal. Ownership is not
    required – any admin within the group suffices.

    Parameters
    ----------
    db:
        Active async session.
    group_id:
        Group identifier.
    user_id:
        The user to be removed.
    current_user:
        The user attempting the operation.

    Raises
    ------
    fastapi.HTTPException
        * 403 – Caller is **not** an admin in the specified group.
    """
    mem_check = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == current_user.id)
    )

    mem = mem_check.scalars().first()
    if not mem or mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail="forbidden")

    stmt = (
        delete(UserGroup)
        .filter(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
    )

    await db.execute(stmt)
    await db.commit()


async def change_user_role_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: GroupRole,
        current_user: User
) -> UserGroup:
    """Update the **role** of a user inside a group (member ↔ admin).

    Only current group **admins** may promote/demote other members. The caller
    cannot change *their own* role to prevent accidental privilege loss.

    Parameters
    ----------
    db:
        Async SQLAlchemy session.
    group_id:
        Target group identifier.
    user_id:
        User whose role will be changed.
    new_role:
        Desired `GroupRole` value.
    current_user:
        Authenticated admin performing the action.

    Returns
    -------
    UserGroup
        Updated a membership object after commit.

    Raises
    ------
    fastapi.HTTPException
        * 403 – Caller lacks admin rights in the group.
        * 404 – Target membership does not exist.
    """
    mem_check = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == current_user.id)
    )

    admin_mem = mem_check.scalars().first()

    if not admin_mem or admin_mem.role != GroupRole.admin:
        raise HTTPException(status_code=403, detail="forbidden")

    stmt = (
        update(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
        .values(role=new_role)
        .returning(UserGroup)
    )
    result = await db.execute(stmt)
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="User not found")

    await db.commit()
    return membership


async def list_group_members(
        db: AsyncSession,
        group_id: uuid.UUID
) -> Sequence[UserGroup]:
    """Return **all** membership rows for the specified group.

    Parameters
    ----------
    db:
        Async SQLAlchemy session.
    group_id:
        Group identifier.

    Returns
    -------
    Sequence[UserGroup]
        Each `UserGroup` row represents a user and their role.
    """
    result = await db.execute(
        select(UserGroup).filter(UserGroup.group_id == group_id)
    )
    return result.scalars().all()


async def is_user_admin_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID
) -> bool:
    """Lightweight helper to check *admin* status.

    Uses ``SELECT role`` only (i.e., no join) for minimal overhead. Suitable for
    **guards** inside higher level services and routers.

    Returns
    -------
    bool
        *True* if the user’s role is `GroupRole.admin`, else *False*.
    """
    result = await db.execute(
        select(UserGroup.role)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    role = result.scalars().first()
    return role == GroupRole.admin


async def is_user_member_in_group(
        db: AsyncSession,
        group_id: uuid.UUID,
        user_id: uuid.UUID
) -> bool:
    """Check whether the user belongs to the group at **any** role level.

    A convenience wrapper around ``SELECT 1 FROM user_groups WHERE … LIMIT 1``.

    Returns
    -------
    bool
        *True* when a row exists, otherwise *False*.
    """
    result = await db.execute(
        select(UserGroup)
        .filter(UserGroup.group_id == group_id, UserGroup.user_id == user_id)
    )
    return bool(result.scalars().first())