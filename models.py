from pydantic import BaseModel
from typing import Optional
from datetime import date

class Todo(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[date] = None