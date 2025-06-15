import pytest
import pytest_asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base, GroupRole
from app.models.user_group import UserGroup
from app.schemas.user import UserCreate
from app.schemas.group import GroupCreate, GroupUpdate
from app.services.user_service import create_user
from app.services.group_service import (
    create_group,
    get_group_by_id,
    list_group_by_user,
    update_group,
    delete_group,
    add_user_to_group,
    remove_user_from_group,
    change_user_role_in_group,
    list_group_members,
    is_user_admin_in_group,
    is_user_member_in_group,
)

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def async_session():
    # Сбрасываем и создаём схему перед каждым тестом
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio(loop_scope="session")
async def test_create_and_get_group(async_session: AsyncSession):
    # Создаём пользователя-владельца
    owner_in = UserCreate(email="owner@example.com", name="Owner", password="pass1234")
    owner = await create_user(async_session, owner_in)

    # Создаём группу
    grp_in = GroupCreate(name="Test Group", description="Test Description")
    group = await create_group(async_session, grp_in, owner.id)

    assert group.id is not None
    assert group.name == "Test Group"
    assert group.owner_id == owner.id

    # Проверяем, что владелец добавлен в группу как admin
    result = await async_session.execute(
        select(UserGroup).where(
            UserGroup.group_id == group.id,
            UserGroup.user_id == owner.id
        )
    )
    membership = result.scalars().first()
    assert membership is not None
    assert membership.role == GroupRole.admin


@pytest.mark.asyncio(loop_scope="session")
async def test_list_groups_for_user(async_session: AsyncSession):
    # Новый владелец и группа
    owner_in = UserCreate(email="owner2@example.com", name="Owner2", password="pass1234")
    owner = await create_user(async_session, owner_in)
    grp_in = GroupCreate(name="Group 2", description="Desc 2")
    group = await create_group(async_session, grp_in, owner.id)

    groups = await list_group_by_user(async_session, owner.id)
    assert len(groups) == 1
    assert groups[0].id == group.id


@pytest.mark.asyncio(loop_scope="session")
async def test_add_change_remove_member(async_session: AsyncSession):
    # Владелец
    owner = await create_user(async_session, UserCreate(
        email="owner3@example.com", name="Owner3", password="pass1234"
    ))
    # Новый участник
    member = await create_user(async_session, UserCreate(
        email="member@example.com", name="Member", password="pass1234"
    ))
    # Группа
    group = await create_group(async_session, GroupCreate(
        name="Group 3", description="Desc 3"
    ), owner.id)

    # Добавляем участника
    membership = await add_user_to_group(async_session, group.id, member.id, role="member")
    assert membership.group_id == group.id
    assert membership.user_id == member.id
    assert membership.role == GroupRole.member

    # Список участников
    members = await list_group_members(async_session, group.id)
    user_ids = {m.user_id for m in members}
    assert owner.id in user_ids
    assert member.id in user_ids

    # Проверка прав и membership-функций
    assert await is_user_member_in_group(async_session, group.id, member.id)
    assert not await is_user_admin_in_group(async_session, group.id, member.id)
    assert await is_user_admin_in_group(async_session, group.id, owner.id)

    # Меняем роль участника на admin
    updated = await change_user_role_in_group(
        async_session, group.id, member.id, new_role=GroupRole.admin, current_user=owner
    )
    assert updated.role == GroupRole.admin
    assert await is_user_admin_in_group(async_session, group.id, member.id)

    # Удаляем участника
    await remove_user_from_group(async_session, group.id, member.id, current_user=owner)
    assert not await is_user_member_in_group(async_session, group.id, member.id)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_and_delete_group(async_session: AsyncSession):
    # Владелец и группа
    owner = await create_user(async_session, UserCreate(
        email="owner4@example.com", name="Owner4", password="pass1234"
    ))
    group = await create_group(async_session, GroupCreate(
        name="Group 4", description="Desc 4"
    ), owner.id)

    # Обновляем группу
    upd = await update_group(async_session, group, GroupUpdate(
        name="Updated Name", description="Updated Desc"
    ), current_user=owner)
    assert upd.name == "Updated Name"
    assert upd.description == "Updated Desc"

    # Удаляем (soft delete)
    await delete_group(async_session, upd, current_user=owner)
    # После soft-delete get_group_by_id должен вернуть None
    fetched = await get_group_by_id(async_session, upd.id)
    assert fetched is None