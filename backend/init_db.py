"""
MongoDB Database Initialization Script.
Run this to set up collections and indexes in MongoDB Atlas.

Usage:
    cd backend
    python init_db.py
"""

from database import get_database
from pymongo import ASCENDING, DESCENDING


def init_database():
    """Initialize MongoDB collections and indexes"""
    print("=" * 50)
    print("MongoDB Database Initialization")
    print("=" * 50)
    
    db = get_database()
    
    if db is None:
        print("\n❌ Failed to connect to MongoDB!")
        print("Check your MONGODB_URI in .env file")
        return False
    
    print(f"\n✅ Connected to database: {db.name}")
    
    # List existing collections
    existing = db.list_collection_names()
    print(f"\nExisting collections: {existing if existing else 'None'}")
    
    # Create user_profiles collection with indexes
    print("\n📁 Setting up 'user_profiles' collection...")
    try:
        profiles = db["user_profiles"]
        
        # Create unique index on user_id
        profiles.create_index(
            [("user_id", ASCENDING)],
            unique=True,
            name="user_id_unique"
        )
        print("   ✅ Created unique index on 'user_id'")
        
        # Create index on email for lookups
        profiles.create_index(
            [("email", ASCENDING)],
            name="email_index"
        )
        print("   ✅ Created index on 'email'")
        
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
    
    # Create search_history collection with indexes
    print("\n📁 Setting up 'search_history' collection...")
    try:
        history = db["search_history"]
        
        # Create compound index for user_id + timestamp queries
        history.create_index(
            [("user_id", ASCENDING), ("timestamp", DESCENDING)],
            name="user_timestamp_index"
        )
        print("   ✅ Created compound index on 'user_id' + 'timestamp'")
        
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
    
    # List final collections
    final_collections = db.list_collection_names()
    print(f"\n📋 Final collections: {final_collections}")
    
    # Show index info
    print("\n📊 Index Information:")
    for coll_name in ["user_profiles", "search_history"]:
        if coll_name in final_collections:
            indexes = list(db[coll_name].list_indexes())
            print(f"\n   {coll_name}:")
            for idx in indexes:
                print(f"      - {idx['name']}: {dict(idx['key'])}")
    
    print("\n" + "=" * 50)
    print("✅ Database initialization complete!")
    print("=" * 50)
    
    return True


if __name__ == "__main__":
    init_database()
