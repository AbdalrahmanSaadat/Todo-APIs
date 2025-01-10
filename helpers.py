
def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"],
        "completed": todo["completed"],
        "due_date": todo["due_date"]
    }