from sqlalchemy.orm import Session
from . import models, schemas
from .logger import get_logger

logger = get_logger(__name__)

# Create
def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(
        title=task.title,
        description=task.description
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    logger.info(f"Task created | id={db_task.id} title={db_task.title}")

    return db_task

# Read (single)
def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


# Read (list)
def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()


# Update
def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    if task_update.title is not None:
        db_task.title = task_update.title

    if task_update.description is not None:
        db_task.description = task_update.description

    if task_update.completed is not None:
        db_task.completed = task_update.completed

    db.commit()
    logger.info(f"Task updated | id={db_task.id}")
    db.refresh(db_task)
    return db_task


# Delete
def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    db.delete(db_task)
    db.commit()
    logger.info(f"Task deleted | id={task_id}")
    return db_task