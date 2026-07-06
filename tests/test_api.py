import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models import User

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
async def auth_token(client):
    response = client.post("/auth/login", json={"username": "test@example.com", "password": "password"})
    assert response.status_code == 200
    return response.json().get("access_token")

@pytest.mark.asyncio
async def test_create_user(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/users/", json={"email": "test@example.com", "name": "Test User"}, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "email": "test@example.com", "name": "Test User"}

@pytest.mark.asyncio
async def test_get_user(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/users/", json={"email": "test@example.com", "name": "Test User"}, headers=headers)
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "email": "test@example.com", "name": "Test User"}

@pytest.mark.asyncio
async def test_create_task(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/users/", json={"email": "test@example.com", "name": "Test User"}, headers=headers)
    response = client.post("/tasks/", json={"title": "Test Task", "description": "A test task", "completed": False, "owner_id": 1}, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "Test Task", "description": "A test task", "completed": False, "owner_id": 1}

@pytest.mark.asyncio
async def test_get_task(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/users/", json={"email": "test@example.com", "name": "Test User"}, headers=headers)
    client.post("/tasks/", json={"title": "Test Task", "description": "A test task", "completed": False, "owner_id": 1}, headers=headers)
    response = client.get("/tasks/1", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Test Task", "description": "A test task", "completed": False, "owner_id": 1}

@pytest.mark.asyncio
async def test_update_task(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/users/", json={"email": "test@example.com", "name": "Test User"}, headers=headers)
    client.post("/tasks/", json={"title": "Test Task", "description": "A test task", "completed": False, "owner_id": 1}, headers=headers)
    response = client.put("/tasks/1", json={"title": "Updated Test Task", "description": "An updated test task", "completed": True, "owner_id": 1}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Updated Test Task", "description": "An updated test task", "completed": True, "owner_id": 1}

@pytest.mark.asyncio
async def test_delete_task(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/users/", json={"email": "test@example.com", "name": "Test User"}, headers=headers)
    client.post("/tasks/", json={"title": "Test Task", "description": "A test task", "completed": False, "owner_id": 1}, headers=headers)
    response = client.delete("/tasks/1", headers=headers)
    assert response.status_code == 204