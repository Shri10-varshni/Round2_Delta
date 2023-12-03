# Task Manager 

This API for managing tasks is implemented using FastAPI for endpoints, SQLite for storing the database and SQLAlchemy to access and manage the data through queries. It uses HS256 algorithm for encryption and Oauth2 for User Authentication.

What does the API do?

You can create an account and add tasks specifying all the parameters that you require. After creating the tasks, you can retirive all your tasks, all your high priority tasks or simply one particular task by specifying its ID. You can also update or mark as done a task that you have now completed. You can either delete any particular task by specifying it's ID or delete all completed tasks in bulk. And when a user no longer wants to use this service, they are free to delete their account which will in turn delete all related data.

The API can be tested with **Swagger UI** which runs on all browsers. 

The following set of libraries are required for the code to run on your system:
1. fastapi (uvicorn server)  - The application is built on FastAPI
2. pydantic  -  Used for Data parsing 
3. sqlalchemy  -  Used to access the database in which the tasks are stored
4. jose - Encoding passowrds and accessing JSON Web Tokens

The following are the steps to run and test the API:
1. Open the terminal in the respective directory
2. Terminal command- uvicorn main:app --reload
3. Copy paste the link in which uvicorn is running (for eg,"http://127.0.0.1:8000") onto your browser
4. Call the /docs endpoint
5. All the endpoints that the API offers is displayed
6. Create an account and start testing the functionalities

The following .py files are used for implementing the code
1. **database.py** -  Code to create an engine and establish connaection to a database
2. **models.py** -  Structure of tables used are defined here
3 **schemas.py** - Response structures for data format using pydantic BaseModel 
4. **crud** - Code for all the functionalities that can be implemented
5. **main** - Endpoints corresponding the functionalities

Update-2 :
User login and authentication was implemented
Few more functionalities were added
 
