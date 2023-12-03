# This file establishes database connection 

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# This stores an instance to the sqlite database (task_api.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./task_api.db"

engine = create_engine(

    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
