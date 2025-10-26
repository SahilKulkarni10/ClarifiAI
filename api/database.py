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
        print(f"🔌 Attempting to connect to MongoDB...")
        print(f"   URI configured: {'Yes' if settings.MONGODB_URI else 'No'}")
        
        if not settings.MONGODB_URI or settings.MONGODB_URI == "mongodb://localhost:27017":
            raise Exception("MongoDB URI not configured or using localhost")
        
        # Create MongoDB client with strict timeouts to prevent hanging
        mongodb.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000,  # 3 second timeout
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        mongodb.database = mongodb.client[settings.DATABASE_NAME]
        
        # Test connection with timeout - wrap in asyncio.wait_for
        await asyncio.wait_for(
            mongodb.client.admin.command('ping'),
            timeout=3.0
        )
        print("✅ Connected to MongoDB Atlas!")
        
        # Create indexes (non-blocking)
        asyncio.create_task(create_indexes())
        
    except asyncio.TimeoutError:
        print(f"❌ MongoDB connection timeout (3s)")
        print("⚠️  API will start without database - set MONGODB_URL environment variable")
        mongodb.client = None
        mongodb.database = None
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️  API will start without database - set MONGODB_URL environment variable")
        # Don't re-raise - let the app start anyway
        mongodb.client = None
        mongodb.database = None

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
