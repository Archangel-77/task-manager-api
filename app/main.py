from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, init_db, close_db
from app.models import User, Task

# Load environment variables (if any)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(lifespan=lifespan)

# -------------------- Authentication --------------------
@app.post("/auth/login")
async def login(credentials: dict, db: AsyncSession = Depends(get_db)):
    username = credentials.get("username")
    password = credentials.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")
    result = await db.execute(select(User).where((User.username == username) | (User.email == username)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # For demonstration purposes, we return a static token
    return {"access_token": "fake-token", "token_type": "bearer"}

# -------------------- User Endpoints --------------------
@app.post("/users/", status_code=201)
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    email = user_data.get("email")
    name = user_data.get("name")
    if not email or not name:
        raise HTTPException(status_code=400, detail="Missing email or name")
    username = email  # Use email as username for simplicity
    hashed_password = "dummy"  # Placeholder; in production hash properly

    # Check for existing user
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar()
    if existing_user:
        return {"id": existing_user.id, "email": existing_user.email, "name": existing_user.name}

    user = User(email=email, username=username, hashed_password=hashed_password, name=name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name}

@app.get("/users/{id}")
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name}

# -------------------- Task Endpoints --------------------
@app.post("/tasks/", status_code=201)
async def create_task(task_data: dict, db: AsyncSession = Depends(get_db)):
    task = Task(**task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "owner_id": task.owner_id,
    }

@app.get("/tasks/{id}")
async def get_task(id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "owner_id": task.owner_id,
    }

@app.put("/tasks/{id}")
async def update_task(id: int, task_data: dict, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_data.items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "owner_id": task.owner_id,
    }

@app.delete("/tasks/{id}")
async def delete_task(id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return Response(status_code=204)

# -------------------- Lifecycle Events --------------------
@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()
