from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

async_engine = create_async_engine(
    url=settings.database_url_asyncpg,
    echo=settings.SQLALCHEMY_ECHO,
    future=True
)

async_sesion_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncSession:

    async with async_sesion_factory() as session:
        yield session