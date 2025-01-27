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
from typing import List
from bson import ObjectId

load_dotenv()

API_IDENTIFIER = os.getenv("API_IDENTIFIER")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

router = APIRouter()

####################### Todo Routes #####################

# Protect the create_todo endpoint
@router.post("/create")
async def create_todo(todo: Todo, token: str = Depends(http_bearer)):
    
    payload = verify_jwt(token.credentials)
    user_id = payload["sub"]  


    try:
        todo.completed = False
        todo.user_id = user_id  

        # to proper addtion the date field to the database
        if todo.due_date:
            todo.due_date = todo.due_date.isoformat()

        
        result = await todo_collection.insert_one(todo.model_dump())
        created_todo = await todo_collection.find_one({"_id": result.inserted_id})
        
        return todo_serializer(created_todo)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())



@router.get("/todos", response_model=List[Todo])
async def get_user_todos(token: str = Depends(http_bearer)):
    try:
        
        payload = verify_jwt(token.credentials)
        user_id = payload["sub"]  

        
        user_todos = await todo_collection.find({"user_id": user_id}).to_list(None)

        
        return [todo_serializer(todo) for todo in user_todos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/todo/{todo_id}", response_model=Todo)
async def get_todo_by_id(todo_id: str, token: str = Depends(http_bearer)):
    try:
        
        payload = verify_jwt(token.credentials)
        user_id = payload["sub"]  

        
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")

        
        todo = await todo_collection.find_one({"_id": ObjectId(todo_id), "user_id": user_id})

        
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found or unauthorized access")

        
        return todo_serializer(todo)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.patch("/todo/{todo_id}", response_model=Todo)
async def update_todo(todo_id: str, updated_fields: dict, token: str = Depends(http_bearer)):
    try:
        
        payload = verify_jwt(token.credentials)
        user_id = payload["sub"]

    
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")

        

        todo = await todo_collection.find_one({"_id": ObjectId(todo_id), "user_id": user_id})
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found or unauthorized access")

        
        if "due_date" in updated_fields:
            try:
                updated_fields["due_date"] = date.fromisoformat(updated_fields["due_date"]).isoformat()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD).")


        
        await todo_collection.update_one(
            {"_id": ObjectId(todo_id), "user_id": user_id},
            {"$set": updated_fields}  
        )

    
        updated_todo = await todo_collection.find_one({"_id": ObjectId(todo_id), "user_id": user_id})
        return todo_serializer(updated_todo)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/todo/{todo_id}", response_model=dict)
async def delete_todo(todo_id: str, token: str = Depends(http_bearer)):
    try:

        payload = verify_jwt(token.credentials)
        user_id = payload["sub"]


        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")


        todo = await todo_collection.find_one({"_id": ObjectId(todo_id), "user_id": user_id})
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found or unauthorized access")


        await todo_collection.delete_one({"_id": ObjectId(todo_id), "user_id": user_id})
        return {"message": "Todo deleted successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/todo/{todo_id}/toggle-completed", response_model=Todo)
async def toggle_todo_completed(todo_id: str, token: str = Depends(http_bearer)):
    try:
        
        payload = verify_jwt(token.credentials)
        user_id = payload["sub"]

        
        if not ObjectId.is_valid(todo_id):
            raise HTTPException(status_code=400, detail="Invalid todo ID format")

        
        todo = await todo_collection.find_one({"_id": ObjectId(todo_id), "user_id": user_id})
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found or unauthorized access")


        updated_completed = not todo["completed"]
        await todo_collection.update_one(
            {"_id": ObjectId(todo_id), "user_id": user_id},
            {"$set": {"completed": updated_completed}}
        )


        updated_todo = await todo_collection.find_one({"_id": ObjectId(todo_id), "user_id": user_id})
        return todo_serializer(updated_todo)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

####################### AUTHENTICATION ROUTES ############################



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

