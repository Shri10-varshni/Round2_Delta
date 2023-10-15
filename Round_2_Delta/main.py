# Main program 

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from models import Base
from schemas import Task, TaskBase
from crud import create_task, delete_task_for_user, get_tasks, update_task_for_user, get_tasks_by_id
from database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Methods performed by the API mapping to the respective endpoints

# Sessionlocal of the db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add_Task (Post method)
@app.post("/add-task/response_model=TaskBase")
def create_task_for_user(
    task: TaskBase, db: Session = Depends(get_db)):
    db_task = create_task(db=db, payload=task)

    # Exception Handling - Internal Server Error
    if db_task is None:
        raise HTTPException(status_code=500, detail="Task ID already exists")

    return db_task

# Get_all_tasks (Get method)
@app.get("/tasks/", response_model=list[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = get_tasks(db, skip=skip, limit=limit)

    # Exception Handling - Not Found
    if tasks is None:
        raise HTTPException(status_code=404, detail="No tasks Found")

    return tasks

# Get_Task_by_TaskID (Get method)
@app.get("/tasks/{id}", response_model = Task)
def read_tasks_by_id(id: int, db: Session = Depends(get_db)):
    task = get_tasks_by_id(db, task_id=id)

    # Exception Handling - Not Found
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

# Update_Task_by_TaskID (Put method)
@app.put("/update-task/{id}", response_model=TaskBase)
def update_task(
    id: int, task: TaskBase, db: Session = Depends(get_db)):
    db_task = update_task_for_user(db=db, task=task, task_id=id)

    # Exception Handling - Not Found
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task

# Delete_Task_by_TaskID (Delete Method)
@app.delete("/delete-task/{id}", response_model=Task)
def delete_task(
   id: int, db: Session = Depends(get_db)):
    db_task = delete_task_for_user(db=db, task_id=id)

    # Exception Handling - Not Found
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task
