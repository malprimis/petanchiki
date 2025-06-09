from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from ..core.config import settings

async_engine = create_async_engine(
    url=settings.database_url_asyncpg
)

async_sesion_factory = async_sessionmaker(async_engine)
