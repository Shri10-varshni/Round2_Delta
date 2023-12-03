# This file contains all the schemas required for data validation

from pydantic import BaseModel
from typing import Optional

from datetime import date, datetime

# Schema for token data 
      
class TokenData(BaseModel):
    user_name: str | None = None

    class Config:
        orm_mode = True


# Schemas for user data
    
class User(BaseModel):
    user_name: str
    full_name: str | None = None
    is_active: bool | None = None

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    user_name: str
    full_name: str | None = None
    password: str

    class Config:
        orm_mode = True
        
class UserInDB(User):
    hashed_password: str

    class Config:
        orm_mode = True

# Schemas for task data

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    reminder: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[str] = None

    class Config:
        orm_mode = True        

class Task(TaskBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True        
