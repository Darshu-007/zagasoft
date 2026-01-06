from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

ALLOWED_ROLES = {"admin", "developer", "intern"}
ALLOWED_STATUS = {"pending", "in_progress", "completed"}

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    assignedTo: int
    dueDate: date


class TaskStatusUpdate(BaseModel):
    status: str
