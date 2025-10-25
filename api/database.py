from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import asyncio

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        # Create MongoDB client without explicit SSL settings to use defaults
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URI)
        mongodb.database = mongodb.client[settings.DATABASE_NAME]
        
        # Test connection
        await mongodb.client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas!")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        # Re-raise the exception instead of going to offline mode
        raise Exception(f"Failed to connect to MongoDB Atlas: {e}")

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("🔌 Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        if not mongodb.database:
            return
            
        # Users collection indexes
        await mongodb.database.users.create_index("email", unique=True)
        await mongodb.database.users.create_index("user_id", unique=True)
        
        # Financial data indexes
        await mongodb.database.income.create_index([("user_id", 1), ("date", -1)])
        await mongodb.database.expenses.create_index([("user_id", 1), ("date", -1)])
        await mongodb.database.investments.create_index([("user_id", 1), ("date", -1)])
        await mongodb.database.loans.create_index([("user_id", 1), ("date", -1)])
        await mongodb.database.insurance.create_index([("user_id", 1), ("date", -1)])
        await mongodb.database.budgets.create_index([("user_id", 1), ("month", -1)])
        
        print("📊 Database indexes created successfully!")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not create indexes: {e}")
        # Continue without indexes - they're for optimization only

def get_database():
    """Get database instance"""
    return mongodb.database
