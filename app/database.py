# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

Base = declarative_base()

# 1. Create async engine
engine = create_async_engine(
    "sqlite+aiosqlite:///./test.db",  # or postgresql+asyncpg, mysql+aiomysql
    echo=True,  # Set to False in production
)

# 2. Create async session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # ← Important!
    autoflush=False,         # ← Important!
)

# 3. Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 4. Initialize tables on startup
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 5. Cleanup on shutdown
async def close_db():
    await engine.dispose()