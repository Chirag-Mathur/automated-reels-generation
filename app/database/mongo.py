"""
MongoDB connection module.
Provides a robust, reusable interface for database access with error handling.
"""
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database
from app.config import settings
from loguru import logger
from typing import Optional

class MongoDBClient:
    """
    MongoDB Client wrapper for safe, reusable access.
    """
    def __init__(self, uri: str):
        self._uri = uri
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = MongoClient(self._uri, serverSelectionTimeoutMS=5000)
            # Attempt to get server info to trigger connection
            self._client.admin.command('ping')
            self._db = self._client.get_default_database()
            logger.info("MongoDB connection established.")
        except errors.PyMongoError as e:
            logger.error(f"MongoDB connection failed: {e}")
            self._client = None
            self._db = None

    def get_db(self) -> Optional[Database]:
        """
        Returns the connected database instance, or None if not connected.
        """
        return self._db

    def get_collection(self, name: str) -> Optional[Collection]:
        """
        Returns a collection by name, or None if not connected.
        """
        if self._db is not None:
            return self._db.get_collection(name)
        logger.error("Attempted to get collection but database is not connected.")
        return None

# Singleton instance for app-wide use
mongo_client = MongoDBClient(settings.MONGO_URI or "")
get_db = mongo_client.get_db
get_collection = mongo_client.get_collection 