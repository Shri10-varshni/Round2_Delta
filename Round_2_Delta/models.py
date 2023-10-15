# Taables(models) required for the API

from sqlalchemy import Column, Integer, String, DateTime, Date

from database import Base

# Structure of the table - Task
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    deadline = Column(Date, index=True, default=None)
    reminder = Column(DateTime, index=True, default=None)
    status = Column(String, index=True, default=None)
    priority = Column(String, index=True, default=None)