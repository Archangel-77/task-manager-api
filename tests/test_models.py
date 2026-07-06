import pytest
from app.models import User, Task

def test_user_model():
    user = User(name="John Doe", email="john@example.com")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"

def test_task_model():
    task = Task(title="Test Task", description="This is a test task.")
    assert task.title == "Test Task"
    assert task.description == "This is a test task."