from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from .logger import get_logger

logger = get_logger(__name__)


SORT_COLUMNS = {
    "created_at": models.Task.created_at,
    "title": models.Task.title,
}


async def create_task(db: AsyncSession, task: schemas.TaskCreate, owner_id: int) -> models.Task:
    db_task = models.Task(
        title=task.title,
        description=task.description,
        owner_id=owner_id,
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    logger.info(f"Task created | id={db_task.id} title={db_task.title}")

    return db_task


async def get_task(db: AsyncSession, task_id: int, owner_id: int) -> models.Task | None:
    result = await db.execute(
        select(models.Task).where(models.Task.id == task_id, models.Task.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    owner_id: int,
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None,
    sort: str = "-created_at",
):
    sort_key = sort.lstrip("-")
    order_col = SORT_COLUMNS[sort_key]
    order_clause = order_col.desc() if sort.startswith("-") else order_col.asc()

    query = select(models.Task).where(models.Task.owner_id == owner_id)
    if completed is not None:
        query = query.where(models.Task.completed == completed)
    query = query.order_by(order_clause).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def count_tasks(db: AsyncSession, owner_id: int, completed: bool | None = None) -> int:
    query = select(func.count()).select_from(models.Task).where(models.Task.owner_id == owner_id)
    if completed is not None:
        query = query.where(models.Task.completed == completed)
    result = await db.execute(query)
    return result.scalar_one()


async def update_task(db: AsyncSession, task_id: int, task_update: schemas.TaskUpdate, owner_id: int):
    db_task = await get_task(db, task_id, owner_id)
    if not db_task:
        return None

    if task_update.title is not None:
        db_task.title = task_update.title

    if task_update.description is not None:
        db_task.description = task_update.description

    if task_update.completed is not None:
        db_task.completed = task_update.completed

    await db.commit()
    logger.info(f"Task updated | id={db_task.id}")
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: int, owner_id: int):
    db_task = await get_task(db, task_id, owner_id)
    if not db_task:
        return None

    await db.delete(db_task)
    await db.commit()
    logger.info(f"Task deleted | id={task_id}")
    return db_task
