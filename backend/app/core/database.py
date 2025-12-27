"""
Database Module
MongoDB Atlas connection and session management.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger

from app.core.config import settings


class Database:
    """
    MongoDB Database connection manager.
    Handles connection lifecycle and provides access to the database instance.
    """
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB Atlas.
        Creates indexes for optimal query performance.
        """
        try:
            self.client = AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000
            )
            
            # Verify connection by pinging the database
            await self.client.admin.command("ping")
            
            self.db = self.client[settings.mongodb_db_name]
            
            # Create indexes for optimal performance
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close the MongoDB connection gracefully.
        """
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """
        Create database indexes for optimal query performance.
        Indexes are created on commonly queried fields.
        """
        try:
            # Users collection indexes
            await self.db.users.create_index("email", unique=True)
            
            # Income collection indexes
            await self.db.income.create_index("user_id")
            await self.db.income.create_index([("user_id", 1), ("date", -1)])
            
            # Expenses collection indexes
            await self.db.expenses.create_index("user_id")
            await self.db.expenses.create_index([("user_id", 1), ("date", -1)])
            await self.db.expenses.create_index([("user_id", 1), ("category", 1)])
            
            # Investments collection indexes
            await self.db.investments.create_index("user_id")
            await self.db.investments.create_index([("user_id", 1), ("type", 1)])
            
            # Loans collection indexes
            await self.db.loans.create_index("user_id")
            
            # Insurance collection indexes
            await self.db.insurance.create_index("user_id")
            
            # Goals collection indexes
            await self.db.goals.create_index("user_id")
            await self.db.goals.create_index([("user_id", 1), ("priority", 1)])
            
            # Chat history collection indexes
            await self.db.chat_history.create_index("user_id")
            await self.db.chat_history.create_index([("user_id", 1), ("timestamp", -1)])
            
            # Recommendation history indexes
            await self.db.recommendations.create_index("user_id")
            await self.db.recommendations.create_index([("user_id", 1), ("created_at", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")


# Global database instance
database = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency function to get the database instance.
    Use with FastAPI's Depends().
    
    Returns:
        The MongoDB database instance
    """
    if database.db is None:
        await database.connect()
    return database.db
