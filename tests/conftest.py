import pytest
from app.database import get_db, Base, engine

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin_nested()
    session = get_db()
    yield session
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    from app.main import app
    with TestClient(app) as client:
        client.app.dependency_overrides[get_db] = lambda: db_session
        yield client