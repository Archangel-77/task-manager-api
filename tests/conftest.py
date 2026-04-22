import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest

TEST_DB_PATH = Path(f"./test_tasks_{uuid4().hex}.db")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["TESTING"] = "1"


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    from app.database import Base, engine

    async def _setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_setup())
    yield

    async def _teardown():
        await engine.dispose()

    asyncio.run(_teardown())
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
