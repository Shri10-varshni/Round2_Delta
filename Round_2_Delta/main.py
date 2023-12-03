# This file contains all the endpoints in the API 

from fastapi import FastAPI, Depends , HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from database import Base, engine, SessionLocal, Session
from schemas import User, UserCreate, Task, TaskBase

# Functions related to the user table and user authentication
from crud import create_account, delete_account, get_users, authenticate_user, create_access_token, get_current_active_user, find_user_id, ACCESS_TOKEN_EXPIRE_MINUTES

# Functions related to the user table
from crud import create_task_for_user, get_all_tasks_for_user, get_tasks_by_id, update_task_for_user, mark_as_done, get_high_priority_tasks, delete_task_for_user, delete_all_completed_tasks

Base.metadata.create_all(engine)   

# An instance of FastAPI is initialised
app = FastAPI()

# Initialising a database session for all endpoints that depend on it
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()     

# User Login (Post method)
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    user = authenticate_user(form_data.username, form_data.password)

    # Exception Handling - Unauthorised user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

# Creates a new account with the data recieved at the user end (Post method)
@app.post("/create-new-account")
def create_new_account(new_user: UserCreate):

    new_user = create_account(new_user=new_user)

    # Exception Handling - Internal Server Error
    if not new_user:
        raise HTTPException(status_code=500, detail="Request failed. Username already exists")

    return {"Status": "Success", "Created_user": new_user}

# Displays the data of all the users in the Table (Get Method)
@app.get("/users/")
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(skip=skip, limit=limit, db=db)

    # Exception Handling - Not Found
    if users is None:
        raise HTTPException(status_code=404, detail="No user Found")

    return users

#------------------------------------------------------------------------------------------------------------------------------------------------#


# Creates and adds the task in the task table through the current user's ID (Post method)
@app.post("/add-task/response_model=TaskBase")
def create_task(
    task: TaskBase, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    db_task = create_task_for_user(db=db, payload=task, user_id=user_id)
    
    return db_task


# Retrieves all the tasks for the particular user (Get method)
@app.get("/tasks/", response_model=list[Task])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    tasks = get_all_tasks_for_user(db = db, user_id = user_id, skip = skip, limit = limit)

    # Exception Handling - Not Found
    if tasks is None:
        raise HTTPException(status_code=404, detail="No tasks Found")

    return tasks

# Retrieves the task pertaining to the particular task ID (Get method)
@app.get("/tasks/{id}", response_model = Task)
def read_tasks_by_id(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)):
    
    user_id = find_user_id(current_user)
    
    task = get_tasks_by_id(db, task_id=id, user_id=user_id)

    # Exception Handling - Not Found
    if task is None:
        raise HTTPException(status_code=404, detail="Invalid Task ID")

    return task   

# Updates the data of the particular task based on the user's input (Put method)
@app.put("/update-task/{id}")
def update_task(
    id: int, 
    task: TaskBase, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    updated_task = update_task_for_user(db=db, task=task, task_id=id, user_id=user_id)

    # Exception Handling - Not Found
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Invalid Task ID")

    return updated_task    

# A pending task whose ID is specified at the user end is marked to be completed (Put method)
@app.put("/markasdone-task/{id}")
def mark_as_done_task(
    id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    db_task = mark_as_done(db=db, task_id=id, user_id=user_id)

    # Exception Handling - Not Found
    if db_task is None:
        raise HTTPException(status_code=404, detail="Invalid Task ID")

    return db_task   

# Retrieves all the high priority tasks of the particular user (Get method)
@app.get("/high-priority-tasks/", response_model=list[Task])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    high_priority_tasks = get_high_priority_tasks(db = db, user_id = user_id, skip = skip, limit = limit)

    # Exception Handling - Not Found
    if high_priority_tasks is None:
        raise HTTPException(status_code=404, detail="No High priority tasks Found")

    return high_priority_tasks


# Deletes the particular task based on the Task ID specified at the user end (Delete Method)
@app.delete("/delete-task/{id}")
def delete_task(
    id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    db_task = delete_task_for_user(db=db, task_id=id, user_id=user_id)

    # Exception Handling - Not Found
    if db_task is None:
        raise HTTPException(status_code=404, detail="Invalid Task ID")

    return db_task

# Deletes all the completed tasks of the particular user (Delete Method)
@app.delete("/delete-completed-tasks/")
def delete_completed_tasks( 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)):

    user_id = find_user_id(current_user)

    db_task = delete_all_completed_tasks(db=db, user_id=user_id)

    return db_task


#------------------------------------------------------------------------------------------------------------------------------------------------#


# Deletes all the data of the particular user and finally the account itself is deleted
@app.delete("/delete-account/")
def delete_task(
    current_user: User = Depends(get_current_active_user)):

    deleted_account = delete_account(current_user)
    
    return deleted_account


