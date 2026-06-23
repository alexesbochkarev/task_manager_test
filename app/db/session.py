from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings


engine = create_async_engine(settings.async_database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
