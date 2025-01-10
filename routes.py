from fastapi import APIRouter,  HTTPException, Depends
from helpers import todo_serializer
from models import Todo, UserCredentials
from database import todo_collection
from pydantic import ValidationError
from datetime import date
from auth0.authentication import Database, GetToken
from auth import verify_jwt, http_bearer, HTTPBearer, get_auth0_client
import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_IDENTIFIER = os.getenv("API_IDENTIFIER")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

router = APIRouter()

# Create a new todo
@router.post("/create")
async def create_todo(todo: Todo):
    try:
        
        todo.completed = False
        
        # to proper addtion the date field to the database
        if todo.due_date:
            todo.due_date = todo.due_date.isoformat()
            
        result = await todo_collection.insert_one(todo.model_dump())
        created_todo = await todo_collection.find_one({"_id": result.inserted_id})
        return todo_serializer(created_todo)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    




@router.post("/register")
async def register_user(credentials: UserCredentials):
    auth0 = get_auth0_client()
    db = Database(AUTH0_DOMAIN, client_id=CLIENT_ID)
    try:
        db.signup(email=credentials.email, password=credentials.password, connection="Username-Password-Authentication")
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/login")
async def login_user(credentials: UserCredentials):
    get_token = GetToken(AUTH0_DOMAIN, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    try:
        token = get_token.login(username=credentials.email, password=credentials.password, realm="Username-Password-Authentication", audience=API_IDENTIFIER)
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
# Test protected route
@router.get("/protected")
async def protected_route(token: str = Depends(http_bearer)):
    payload = verify_jwt(token.credentials)
    return {"message": "You are authorized", "user": payload}

