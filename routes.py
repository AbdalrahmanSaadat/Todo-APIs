from fastapi import APIRouter,  HTTPException
from helpers import todo_serializer
from models import Todo
from database import todo_collection
from pydantic import ValidationError
from datetime import date


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
    
    
