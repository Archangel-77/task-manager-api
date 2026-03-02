# Task Manager API

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

## Docker (API + PostgreSQL)

1. Create `.env` from `.env.example`
2. Start services:

```powershell
docker compose up --build
```

API: <http://127.0.0.1:8000>

## Deployment

The repository includes a `Procfile` for PaaS platforms that run process commands directly.

```text
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
