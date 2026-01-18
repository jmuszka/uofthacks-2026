"""
MongoDB database operations for Trovato.
Handles user profiles and search history.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone
from typing import Optional, Dict, Any

load_dotenv()

_client = None
_db_name = "Travado"


def get_database():
    """Get MongoDB database connection (lazy singleton)"""
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            print("Error: MONGODB_URI not found in environment variables.")
            return None
        try:
            _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            _client.admin.command('ping')
            print("Connected to MongoDB.")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            _client = None
    
    if _client:
        return _client[_db_name]
    return None


# =============================================================================
# USER PROFILE OPERATIONS
# =============================================================================

def upsert_user_profile(profile_data: Dict[str, Any]) -> bool:
    """
    Create or update a user profile.
    Uses user_id as the unique identifier for upsert.
    Returns True on success, False on failure.
    """
    db = get_database()
    if db is None:
        print("Database unavailable, cannot save profile.")
        return False

    try:
        collection = db["user_profiles"]
        user_id = profile_data.get("user_id")
        
        if not user_id:
            print("Error: user_id is required for profile upsert")
            return False
        
        # Set timestamps
        now = datetime.now(timezone.utc)
        profile_data["updated_at"] = now
        
        # Check if profile exists to set created_at appropriately
        existing = collection.find_one({"user_id": user_id})
        if existing:
            profile_data["created_at"] = existing.get("created_at", now)
        else:
            profile_data["created_at"] = now
        
        # Upsert the profile
        result = collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        
        print(f"Profile upserted for user {user_id}")
        return True
    except Exception as e:
        print(f"Error upserting profile: {e}")
        return False


def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user profile by user_id.
    Returns the profile dict or None if not found.
    """
    if not user_id:
        return None

    db = get_database()
    if db is None:
        return None

    try:
        collection = db["user_profiles"]
        profile = collection.find_one({"user_id": user_id})
        
        if profile:
            # Convert ObjectId to string for JSON serialization
            profile["_id"] = str(profile["_id"])
            return profile
        return None
    except Exception as e:
        print(f"Error retrieving profile: {e}")
        return None


def delete_user_profile(user_id: str) -> bool:
    """
    Delete a user profile by user_id.
    Returns True if deleted, False otherwise.
    """
    if not user_id:
        return False

    db = get_database()
    if db is None:
        return False

    try:
        collection = db["user_profiles"]
        result = collection.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            print(f"Deleted profile for user {user_id}")
            return True
        return False
    except Exception as e:
        print(f"Error deleting profile: {e}")
        return False


def get_all_profiles(limit: int = 100) -> list:
    """
    Retrieve all user profiles (for admin/debugging).
    """
    db = get_database()
    if db is None:
        return []

    try:
        collection = db["user_profiles"]
        cursor = collection.find().limit(limit)
        
        profiles = []
        for profile in cursor:
            profile["_id"] = str(profile["_id"])
            profiles.append(profile)
        return profiles
    except Exception as e:
        print(f"Error retrieving profiles: {e}")
        return []


# =============================================================================
# SEARCH HISTORY OPERATIONS
# =============================================================================

def add_search_history(user_id: str, query: str):
    """
    Adds a search query to the user's history.
    """
    if not user_id or not query:
        return

    db = get_database()
    if db is None:
        print("Database unavailable, skipping history save.")
        return

    try:
        collection = db["search_history"]
        doc = {
            "user_id": user_id,
            "query": query,
            "timestamp": datetime.now(timezone.utc)
        }
        collection.insert_one(doc)
        print(f"Saved search history for user {user_id}")
    except Exception as e:
        print(f"Error saving search history: {e}")


def get_search_history(user_id: str, limit: int = 5):
    """
    Retrieves the most recent search history for a user.
    """
    if not user_id:
        return []

    db = get_database()
    if db is None:
        return []

    try:
        collection = db["search_history"]
        cursor = collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return [doc["query"] for doc in cursor]
    except Exception as e:
        print(f"Error retrieving search history: {e}")
        return []
