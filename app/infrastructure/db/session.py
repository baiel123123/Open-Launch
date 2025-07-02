from contextlib import asynccontextmanager

from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.config import get_database_settings

async_url = get_database_settings().async_url
engine = create_async_engine(async_url,
                             pool_pre_ping=True,
                             poolclass=AsyncAdaptedQueuePool,
                             pool_size=1,
                             max_overflow=1)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    session = session_maker()
    async with session.begin():
        yield session


async def shutdown() -> None:
    if engine is not None:
        await engine.dispose()
