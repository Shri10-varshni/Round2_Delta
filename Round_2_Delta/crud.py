# This file contains all the necessary functions for smooth exceution at the endpoint

from datetime import datetime, timedelta
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from database import Session, SessionLocal
from models import Userdb, Taskdb
from schemas import TokenData, UserCreate, User, TaskBase


SECRET_KEY = "00f73470e53d6bbd83ff23e0a14c4e688d4f64ca4ffb2faa14c9180eae33e194"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   


# Hashes the password
def get_hashed_password(password):
    return pwd_context.hash(password)

# Verifies if the plain password matches with the hased password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Creates an access token that expires in a specified amount of time
def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt    

# Retrieves the user data from the database for the specified username   
def get_user(user_name: str): 
    
    db = SessionLocal()
    user_data = db.query(Userdb).filter(Userdb.user_name == user_name).first()  
    db.close()  

    return user_data

# Authenticates the user given the username and password
def authenticate_user(user_name: str, password: str):

    user = get_user(user_name=user_name)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user

# Updates the active status of a user (Pass the data of the authenticated user)
def update_active_status(user: Userdb):
    #db = SessionLocal()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    #db_user = db.query(Userdb).filter(Userdb.user_name == user.user_name).first()

    if user.is_active is False:
        user.is_active = True

    #if db_user.is_active is False:
        #db_user.is_active = True

    #db.commit()   
    #db.refresh(db_user)
    #db.close()
    return user

# Gets the data of the user who is currently logged-in
def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        token_data = TokenData(user_name=user_name)
    except JWTError:
        raise credentials_exception

    user = get_user(user_name=token_data.user_name)
    
    if user is None:
        raise credentials_exception

    user = update_active_status(user)

    return user

# Gets the active user which depends on the current user
def get_current_active_user(current_user: User = Depends(get_current_user)):

    if current_user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

#------------------------------------------------------------------------------------------------------------------------------------------------#


# Returns the user ID corresponding to the particular user
def find_user_id(current_user: User):

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    user_data = get_user(user_name = current_user.user_name)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not Found")
    
    user_id = user_data.user_id

    return user_id

# Creates a new account and stores in the Userdb table
def create_account(new_user: UserCreate):

    db = SessionLocal()
    hashed_password = get_hashed_password(new_user.password)

    user_exists = get_user(new_user.user_name)

    if user_exists:
        return None  # Returns None if user_name already exists

    db_user = Userdb(user_name=new_user.user_name, full_name=new_user.full_name, hashed_password=hashed_password)    

    db.add(db_user)
    db.commit()
    db.flush()
    
    new_user = db.query(Userdb).filter(Userdb.user_name == new_user.user_name).first()
    
    return new_user

# Retrieves all the users in the Table Userdb
def get_users(db: Session, skip: int = 0, limit: int = 100):

    db_users = db.query(Userdb).offset(skip).limit(limit).all()

    if db_users == []:
        return None  # Returns None if no user is found

    return db_users

# Deletes the account and the account data corresponding to the particular user
def delete_account(current_user: User):

    db = SessionLocal()

    user_id = find_user_id(current_user)
    user_tasks = db.query(Taskdb).filter(Taskdb.user_id == user_id).all()
    
    if user_tasks == []:
        pass
    else:
        for task in user_tasks:
            db.delete(task)
            db.commit()

    delete_user = get_user(current_user.user_name)
    db.delete(delete_user)
    db.commit()

    return {"Status": "Success", "Detail" : "All Tasks in your account were deleted", "Final":"Account deleted successfully"}

#------------------------------------------------------------------------------------------------------------------------------------------------#


# Retrieves all tasks in the Tasks table
def get_all_tasks_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    db_tasks = db.query(Taskdb).filter(Userdb.user_id == user_id).offset(skip).limit(limit).all()
    if db_tasks == []:
        return None  # Returns None if no task is found
    return db_tasks

# Retrieves the task details mapping to the the task ID if in Task Table
def get_tasks_by_id(db: Session, task_id: int, user_id: int):
    
    db_task = db.query(Taskdb).filter(Taskdb.user_id == user_id, Taskdb.id == task_id).first()
    
    if db_task is None:
        return None  # Returns None if Task ID is not found
    
    return db_task

# New Task is inserted into Task Table
def create_task_for_user(payload: TaskBase, db: Session, user_id: int):
    try:
        new_task = Taskdb(**payload.dict())
        new_task.user_id = user_id

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        db_new_task = get_tasks_by_id(db, new_task.id, user_id)

        if not db_new_task:
            return {"Status": "Failed", "Detail": "Couldn't Create new Task"}
    
        return {"Status": "Success", "Created_Task": db_new_task}   

    except Exception:
        raise HTTPException(status_code=422, detail=str(Exception))

# Updates an already existing Task in the Task Table
def update_task_for_user(db: Session, task_id: int, task: TaskBase, user_id: int):

    db_task = get_tasks_by_id(db, task_id, user_id)

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

    return {"Status": "Success", "Detail":"Task_Updated"}

# An already existing task is marked as done
def mark_as_done(db: Session, task_id: int, user_id: int):  

    db_task = get_tasks_by_id(db, task_id, user_id)

    if db_task is None:
        return None  # Returns None if Task ID is not found

    db_task.status = "Completed"  

    db.commit()
    db.refresh(db_task)

    return {"Status": "Success", "Detail":"Task_Marked_Done"}

# Retrieves all high priority tasks
def get_high_priority_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):

    db_tasks = db.query(Taskdb).filter(Taskdb.user_id == user_id, Taskdb.priority == "High").offset(skip).limit(limit).all()

    if db_tasks == []:
        return None  # Returns None if no task is found

    return db_tasks

# Deletes an already existing Task from the Task Table
def delete_task_for_user(db: Session, task_id: int, user_id: int):

    db_task = get_tasks_by_id(db, task_id, user_id)

    if db_task is None:
        return None  # Returns None if Task ID is not found

    db.delete(db_task)
    db.commit()

    return {"Status": "Success", "Detail" : "Task_Deleted"}

# Deletes all completed Tasks from the Task Table
def delete_all_completed_tasks(db: Session, user_id: int):

    completed_tasks = db.query(Taskdb).filter(Taskdb.user_id == user_id, Taskdb.status == "Completed").all()
    
    count_completed_tasks = len(completed_tasks)

    if completed_tasks == []:
        return {"Message":"No completed tasks found"}
    else:
        for task in completed_tasks:
            db.delete(task)
            db.commit()
    return {"Status":"Success", "Detail":f"{count_completed_tasks} completed tasks were deleted"}        
