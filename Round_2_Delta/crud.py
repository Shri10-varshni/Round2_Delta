# Functions performed in the Tasks Table(model)

from sqlalchemy.orm import Session

import models
import schemas

# Retrieves all tasks in the Tasks table
def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    db_tasks = db.query(models.Task).offset(skip).limit(limit).all()
    if db_tasks == []:
        return None  # Returns None if no task is found
    return db_tasks

# Retrieves the task details mapping to the the task ID if in Task Table
def get_tasks_by_id(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None  # Returns None if Task ID is not found
    return db_task

# New Task is inserted into Task Table
def create_task(payload: schemas.TaskBase, db: Session):
    new_note = models.Task(**payload.dict())
    db_task = db.query(models.Task).filter(models.Task.id == new_note.id).first()
    if db_task is not None:
        return None  # Returns None if Task ID already exists
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {"Status": "Success", "Created_Task": new_note}

# Deletes an already existing Task from the Task Table
def delete_task_for_user(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None  # Returns None if Task ID is not found
    db.delete(db_task)
    db.commit()
    return {"Status": "Success", "Deleted_Task": db_task}

# Updates an already existing Task in the Task Table
def update_task_for_user(db: Session, task_id: int, task: schemas.TaskBase):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None  # Returns None if Task ID is not found
    db_task.name = task.name
    db_task.description = task.description
    db_task.deadline = task.deadline
    db_task.reminder = task.reminder
    db_task.status = task.status
    db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)
    return {"Status": "Success", "Updated_Task": db_task}