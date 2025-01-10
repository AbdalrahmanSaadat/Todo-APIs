from motor.motor_asyncio import AsyncIOMotorClient
from google.cloud import secretmanager
import os
from dotenv import load_dotenv

###################### Local Tesing

# load_dotenv()

# MONGODB_URI = os.getenv("MONGODB_URI")

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



##################### Production


def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/todo-447413/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

MONGODB_URI = get_secret("MONGODB_URI")

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


DB_NAME = "todo_db"

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
todo_collection = db["data"]
