# backend/database.py

from pymongo import MongoClient

try:
    from backend.config import MONGODB_URI, MONGODB_DB_NAME
except ModuleNotFoundError:
    from config import MONGODB_URI, MONGODB_DB_NAME

# Setup MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]

# Expose database and messages collection
messages_collection = db["messages"]

def get_db():
    return db