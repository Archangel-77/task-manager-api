import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from ..app.database import engine, Base
from app.main import app

@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

@pytest.fixture
def db_session() -> AsyncSession:
    connection = engine.connect()
    transaction = connection.begin_nested()
    session: AsyncSession = get_db()
    yield session
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()