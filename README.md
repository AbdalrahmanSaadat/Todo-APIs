# Todo-APIs
Todo list simple CRUD using FastAPI for Backend, MongoDb for database, and Auth0 for Authorization.

# Description
A simple Todo List APIs, You shoild register first to be authorized to use the APIs, after registration you could login and create a Todo Task with a title and due date if you want, you could switch the completion status via another seperated endpoint for more convenient approach.


# Instructions
To run the project locally you could use the following command after make sure you installed required libiraries from requirements file:


uvicorn main:app --reload


then you could test all endpoints via local server:

http://127.0.0.1:8000/{route}
# How to deploy The project on Google Cloud Services?
Prepare the requirements file


Create account on google Cloud Services


Create a project with the name you want


Install Google Cloud SDK


Initialize  Google Cloud SDK Using command: gcloud init


Create app.yaml file to configure the app on Google Cloud 


Deply the app using this command: gcloud app deploy


to monitor and see logs use command: gcloud app logs tail -s default



# Postman collection
Each folder include a specific action alongside with it's all possible 

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/34871237-eda7ac29-e344-475a-b721-a83f0267d569?source=rip_markdown&collection-url=entityId%3D34871237-eda7ac29-e344-475a-b721-a83f0267d569%26entityType%3Dcollection%26workspaceId%3D85bfcce8-cee8-4e40-9e54-7c30313fb904)


# Project Public Link
https://todo-447413.uc.r.appspot.com


# Security Notes
While testing locally I used .env file to store the Database URL


While testing on production I used Google Cloud Secret Manager


Database is reacheable via the connection link using (MongoDB Atlas), that link is secured due to it contain the password of the database.

