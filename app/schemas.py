from datetime import datetime
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing import Annotated, Optional

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)]


class TaskBase(BaseModel):
    title: Title
    description: Optional[Description] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[Title] = None
    description: Optional[Description] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
