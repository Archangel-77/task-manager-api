from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import crud, models, schemas
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_user_by_username,
    hash_password,
)
from .database import Base, engine, get_db
from .logger import configure_logging

configure_logging()

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Task Manager API running"}


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = models.User(username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks/", response_model=schemas.TaskResponse)
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await crud.create_task(db, task, owner_id=current_user.id)


@app.get("/tasks/", response_model=List[schemas.TaskResponse])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None,
    sort: str = "-created_at",
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tasks = await crud.get_tasks(
        db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        completed=completed,
        sort=sort,
    )
    if tasks is None:
        raise HTTPException(status_code=400, detail="Invalid sort value. Use: created_at, -created_at, title, -title")
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_task = await crud.get_task(db, task_id, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_task = await crud.update_task(db, task_id, task_update, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_task = await crud.delete_task(db, task_id, owner_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
