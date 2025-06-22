from datetime import datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def async_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def async_client(async_session):
    # Подменяем зависимость get_db
    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db

    # Используем ASGITransport для работы с FastAPI-приложением
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio(loop_scope="session")
async def test_full_flow(async_client):
    # --- 1) Регистрация ---
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "name": "Alice", "password": "secret123"}
    )
    assert resp.status_code == 201
    user = resp.json()
    assert user["email"] == "alice@example.com"
    user_id = user["id"]

    # --- 2) Логин ---
    resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "alice@example.com", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # --- 3) GET /users/me ---
    resp = await async_client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == user_id

    # --- 4) Создание группы ---
    resp = await async_client.post(
        "/api/v1/groups/",
        json={"name": "Test Group", "description": "Desc"},
        headers=auth_headers
    )
    assert resp.status_code == 201
    group = resp.json()
    group_id = group["id"]

    # --- 5) Список своих групп ---
    resp = await async_client.get("/api/v1/groups/", headers=auth_headers)
    assert resp.status_code == 200
    assert any(g["id"] == group_id for g in resp.json())

    # --- 6) Создание категории ---
    resp = await async_client.post(
        f"/api/v1/groups/{group_id}/categories",
        json={"name": "Food", "icon": "🍔"},
        headers=auth_headers
    )
    assert resp.status_code == 201
    category_id = resp.json()["id"]

    # --- 7) Список категорий ---
    resp = await async_client.get(f"/api/v1/groups/{group_id}/categories", headers=auth_headers)
    assert resp.status_code == 200
    assert any(c["id"] == category_id for c in resp.json())

    # --- 8) Создание транзакции ---
    tx_payload = {
        "group_id": group_id,
        "category_id": category_id,
        "amount": 42.5,
        "type": "expense",
        "description": "Lunch",
        "date": datetime.now().isoformat()
    }
    resp = await async_client.post("/api/v1/transactions", json=tx_payload, headers=auth_headers)
    assert resp.status_code == 201
    tx_id = resp.json()["id"]

    # --- 9) Получить транзакцию по ID ---
    resp = await async_client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == tx_id

    # --- 10) Обновить транзакцию ---
    resp = await async_client.patch(
        f"/api/v1/transactions/{tx_id}",
        json={"description": "Dinner", "amount": 50.0},
        headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 50.0 and data["description"] == "Dinner"

    # --- 11) Список транзакций с фильтрами ---
    resp = await async_client.get(
        "/api/v1/transactions",
        params={"group_id": group_id, "skip": 0, "limit": 10},
        headers=auth_headers
    )
    assert resp.status_code == 200
    assert any(t["id"] == tx_id for t in resp.json())

    # --- 12) Удаление транзакции ---
    resp = await async_client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert resp.status_code == 204
    resp = await async_client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert resp.status_code == 404
