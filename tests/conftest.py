import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from app.models import Base  # Add this line to import Base
from app.main import app, get_db  # Import app and get_db from main.py

# 1. Create test DB engine
@pytest_asyncio.fixture(scope="function", name="db_engine")  # Define the correct return type
async def db_engine() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

# 2. Create test DB session
@pytest_asyncio.fixture(scope="function", name="db_session")  # Define the correct return type
async def db_session(db_engine: AsyncEngine) -> AsyncSession:
    TestSessionLocal = async_sessionmaker(bind=db_engine, class_=AsyncSession)
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

# 3. Override FastAPI dependency
@pytest_asyncio.fixture(scope="function", name="client")  # Define the correct return type
async def client(db_session: AsyncSession) -> AsyncClient:
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()

# 4. Write async tests
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/users/", json={"email": "test@example.com"})
    assert response.status_code == 201