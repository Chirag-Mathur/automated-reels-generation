from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI)
db = client.get_default_database() 