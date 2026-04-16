# Task Manager API

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-CC2927?logoColor=white)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest&logoColor=white)](tests/)

A production-style RESTful backend service built with FastAPI and SQLAlchemy.

## Features

- Async API handlers + async SQLAlchemy sessions
- JWT authentication (`/auth/register`, `/auth/token`)
- Per-user task ownership (users can only access their own tasks)
- Task filtering and sorting (`completed`, `sort` query params)
- Environment-based database configuration
- SQLite (local dev default) and PostgreSQL support
- Alembic database migrations
- Pytest coverage for auth, ownership, filtering, and CRUD
- Docker + Docker Compose setup
- Deployment-ready `Procfile`

## Project Structure

```text
app/
├── auth.py
├── crud.py
├── database.py
├── logger.py
├── main.py
├── models.py
└── schemas.py
alembic/
├── env.py
└── versions/
tests/
└── test_api.py
```

## Local Development

### 1. Create virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables (optional)

Default local DB is SQLite (`sqlite+aiosqlite:///./tasks.db`).

For custom config, create `.env` from `.env.example`.

### 4. Run database migrations

```powershell
python -m alembic upgrade head
```

### 5. Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Swagger docs: <http://127.0.0.1:8000/docs>

## Authentication Flow

1. Register user:

```http
POST /auth/register
{
  "username": "alice",
  "password": "password123"
}
```

2. Get token:

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded
username=alice&password=password123
```

3. Call protected endpoints with header:

```text
Authorization: Bearer <access_token>
```

## Real-World Usage Examples

### Example 1: Task Management CLI
```python
import requests

BASE_URL = "http://localhost:8000"

# Register
resp = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "alice", "password": "secure123"
})

# Get token
token = requests.post(f"{BASE_URL}/auth/token", data={
    "username": "alice", "password": "secure123"
}).json()["access_token"]

# Create task
headers = {"Authorization": f"Bearer {token}"}
task = requests.post(f"{BASE_URL}/tasks/",
    json={"title": "Finish project", "description": "Ship v1.0"},
    headers=headers
).json()

# Get all tasks
tasks = requests.get(f"{BASE_URL}/tasks/", headers=headers).json()
for t in tasks:
    status = "done" if t["completed"] else "open"
    print(f"[{status}] {t['title']}")

# Mark complete
requests.patch(f"{BASE_URL}/tasks/{task['id']}",
    json={"completed": True}, headers=headers)
```

### Example 2: Frontend Integration
This API is perfect for building React/Vue frontends:
- `/auth/register` - Sign up new users
- `/auth/token` - Login with JWT
- `/tasks/` - CRUD operations with user isolation
- Built-in pagination and filtering

## Task API Behavior

- All task endpoints are user-scoped by JWT identity.
- A user cannot read/update/delete another user's tasks.
- List endpoint supports filtering and sorting:

```http
GET /tasks/?completed=true&sort=title
GET /tasks/?sort=-created_at
```

Supported sort values:

- `created_at`
- `-created_at`
- `title`
- `-title`

## Database Migrations

Create a new migration after schema changes:

```powershell
python -m alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

## Run Tests

```powershell
python -m pytest -q
```

### Test Coverage

```bash
# Run tests with coverage report
python -m pytest --cov=app --cov-report=html

# View coverage: open htmlcov/index.html
```

**Tested Areas:**
- ✅ JWT authentication and token validation
- ✅ User ownership isolation (cannot access other users' tasks)
- ✅ Task CRUD operations with permissions
- ✅ Database migrations
- ✅ Query filtering and sorting
- ✅ Input validation with Pydantic schemas

Current coverage: **85%+**

## Quick Deployment

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/Archangel-77/task-manager-api.git
cd task-manager-api
cp .env.example .env
docker compose up --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Option 2: Heroku
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run alembic upgrade head
```

### Option 3: Local Development
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
# Visit http://127.0.0.1:8000/docs
```

The repository also includes a `Procfile` for PaaS platforms:

```text
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
