"""Test MongoDB connection and help identify connection details."""
from __future__ import annotations

import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


def test_connection(uri: str, db_name: str = "traffic_analytics") -> None:
    """Test MongoDB connection with given URI."""
    try:
        print(f"Testing connection to: {uri}")
        print(f"Database: {db_name}")
        print("-" * 50)
        
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Get database
        db = client[db_name]
        
        # List collections
        collections = db.list_collection_names()
        print(f"\n📊 Collections found: {collections}")
        
        # Count documents
        if "traffic_raw" in collections:
            count = db.traffic_raw.count_documents({})
            print(f"   - traffic_raw: {count} documents")
        
        if "traffic_summary" in collections:
            count = db.traffic_summary.count_documents({})
            print(f"   - traffic_summary: {count} documents")
        
        # Get connection info
        print(f"\n🔗 Connection details:")
        print(f"   - Host: {client.address}")
        print(f"   - Database: {db_name}")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("  1. MongoDB is not running")
        print("  2. Wrong connection URI")
        print("  3. Network/firewall issues")
        return False
        
    except OperationFailure as e:
        print(f"❌ Authentication failed: {e}")
        print("\nYou need to provide username and password.")
        print("Format: mongodb://username:password@host:port/")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 50)
    print("MongoDB Connection Tester")
    print("=" * 50)
    print()
    
    # Test common connection strings
    test_uris = [
        ("mongodb://localhost:27017/", "Local MongoDB (no auth)"),
        ("mongodb://127.0.0.1:27017/", "Local MongoDB (no auth, IP)"),
    ]
    
    print("Testing common local connections...")
    print()
    
    for uri, description in test_uris:
        print(f"Testing: {description}")
        if test_connection(uri):
            print(f"\n✅ Success! Use this connection string:")
            print(f"   MONGODB_URI={uri}")
            return
        print()
    
    print("\n" + "=" * 50)
    print("If you're using MongoDB Atlas (cloud):")
    print("=" * 50)
    print("1. Go to MongoDB Atlas dashboard")
    print("2. Click 'Connect' on your cluster")
    print("3. Choose 'Connect your application'")
    print("4. Copy the connection string")
    print("5. Replace <password> with your actual password")
    print("6. Format: mongodb+srv://username:password@cluster.mongodb.net/")
    print()
    print("If you're using local MongoDB with authentication:")
    print("1. Check your mongod.conf file for auth settings")
    print("2. Or create a user: db.createUser({user: 'username', pwd: 'password', roles: ['readWrite']})")
    print()


if __name__ == "__main__":
    main()

