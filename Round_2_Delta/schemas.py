# Schemas required for various task functionalities

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class TaskBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    reminder: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[str] = None

    class Config:
        orm_mode = True


class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True