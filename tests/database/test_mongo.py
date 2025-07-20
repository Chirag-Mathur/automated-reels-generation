"""
Tests for MongoDB connection and database utilities.
"""
import pytest
from app.database.mongo import mongo_client
from pymongo import errors


def mongo_connection_ok(client) -> bool:
    """
    Tests the MongoDB connection. Returns True if successful, False otherwise.
    """
    if not getattr(client, '_client', None):
        print("No client object")
        return False
    try:
        client._client.admin.command('ping')
        return True
    except Exception as e:
        print("MongoDB connection error:", e)
        return False

def test_mongo_connection():
    """
    Test that the MongoDB connection can be established.
    """
    assert mongo_connection_ok(mongo_client) is True, "MongoDB connection failed" 