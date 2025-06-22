from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import (
    auth,
    users,
    groups,
    categories,
    transactions,
)
from app.core.config import settings
from app.db.session import (
    async_engine,
)
from app.utils.logger import setup_logging

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # === startup ===
    # 1) Создаём таблицы (только в dev; в prod — миграции через Alembic)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield

    await async_engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=settings.OPENAPI_URL,      # например "/api/v1/openapi.json"
    docs_url=settings.DOCS_URL,            # например "/docs"
    redoc_url=settings.REDOC_URL,          # например "/redoc"
    lifespan=lifespan
)

# CORS: по умолчанию пустой список
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем наши маршруты
app.include_router(auth.router,        prefix="/api/v1")
app.include_router(users.router,       prefix="/api/v1")
app.include_router(groups.router,      prefix="/api/v1")
# категории и транзакции — пути уже внутри роутеров включают /groups или /transactions
app.include_router(categories.router,  prefix="/api/v1")
app.include_router(transactions.router,prefix="/api/v1")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API (v{settings.VERSION})"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # для локальной разработки
    )