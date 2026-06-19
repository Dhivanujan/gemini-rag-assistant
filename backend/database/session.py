# backend/database/session.py

from pymongo import MongoClient
from backend.core.config import MONGODB_URI, MONGODB_DB_NAME

# Setup MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]

# Expose messages collection for database operations
messages_collection = db["messages"]

def get_db():
    return db
