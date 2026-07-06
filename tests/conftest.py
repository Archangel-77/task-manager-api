import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base
from typing import AsyncGenerator

DATABASE_URL = "sqlite+aiosqlite:///./alembic/alembic.db"
engine = create_async_engine(DATABASE_URL, echo=True)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session