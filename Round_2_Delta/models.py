# This files contains the structure of all the tables used for storing data in this API

from database import Base 
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship

# Structure of the Table to store user data
class Userdb(Base):

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)

    # Establishing a one-to-many relationship with TaskDb
    tasks = relationship("Taskdb", back_populates="user")

# Structure of the table to store Task data
class Taskdb(Base):

    __tablename__ = "tasks"

    id = Column(Integer, auto_increment=True, primary_key=True, index=True)
    name = Column(String, index=True, default='Untitled Task')
    description = Column(String, index=True, default=None)
    deadline = Column(Date, index=True, default=None)
    reminder = Column(DateTime, index=True, default=None)
    status = Column(Enum('Pending', 'Completed'), index=True, default='Pending')
    priority = Column(Enum('High', 'Medium', 'Low'), index=True, default='Medium')

    # Establishing a many-to-one relationship with UserDb
    user_id = Column(Integer, ForeignKey(Userdb.user_id))
    user = relationship("Userdb", back_populates="tasks")
