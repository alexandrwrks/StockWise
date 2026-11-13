from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

new_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with new_session() as session:
        yield session