"""MongoDB connection and database utilities."""
from __future__ import annotations

import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure


def get_mongo_uri() -> str:
    """Get MongoDB connection URI from environment or use default.
    
    For local MongoDB (no auth): mongodb://localhost:27017/
    For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/
    For local with auth: mongodb://username:password@localhost:27017/
    """
    return os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017/",  # Default: local MongoDB without authentication
    )


def get_database_name() -> str:
    """Get database name from environment or use default."""
    return os.getenv("MONGODB_DATABASE", "traffic_analytics")


def get_mongo_client() -> MongoClient:
    """Create and return a MongoDB client."""
    uri = get_mongo_uri()
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except ConnectionFailure as e:
        raise ConnectionFailure(
            f"Failed to connect to MongoDB at {uri}. "
            f"Make sure MongoDB is running. Error: {e}"
        ) from e


def get_database(db_name: Optional[str] = None) -> Database:
    """Get MongoDB database instance."""
    client = get_mongo_client()
    name = db_name or get_database_name()
    return client[name]

