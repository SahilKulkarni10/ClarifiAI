"""
Authentication Service
Handles user registration, login, and profile management.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfile,
    UserProfileUpdate,
    PasswordUpdate,
    AuthResponse
)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users
    
    async def register(self, user_data: UserCreate) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            AuthResponse with access token and user info
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user document
        now = datetime.utcnow()
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "hashed_password": get_password_hash(user_data.password),
            "created_at": now,
            "updated_at": now
        }
        
        # Insert into database
        result = await self.collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        logger.info(f"New user registered: {user_data.email}")
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        # Build response
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user_id,
                user_id=user_id,
                email=user_data.email,
                name=user_data.name,
                created_at=now.isoformat()
            )
        )
    
    async def login(self, credentials: UserLogin) -> AuthResponse:
        """
        Authenticate a user and return tokens.
        
        Args:
            credentials: Login credentials (email and password)
            
        Returns:
            AuthResponse with access token and user info
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        user = await self.collection.find_one({"email": credentials.email})
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            raise ValueError("Invalid email or password")
        
        user_id = str(user["_id"])
        
        logger.info(f"User logged in: {credentials.email}")
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        # Build response
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user_id,
                user_id=user_id,
                email=user["email"],
                name=user["name"],
                created_at=user.get("created_at", datetime.utcnow()).isoformat()
            )
        )
    
    async def get_profile(self, user_id: str) -> UserProfile:
        """
        Get user profile by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            UserProfile object
            
        Raises:
            ValueError: If user not found
        """
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = await self.collection.find_one({"_id": user_id})
        
        if not user:
            raise ValueError("User not found")
        
        return UserProfile(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            created_at=user.get("created_at", datetime.utcnow()).isoformat()
        )
    
    async def update_profile(
        self,
        user_id: str,
        update_data: UserProfileUpdate
    ) -> UserProfile:
        """
        Update user profile.
        
        Args:
            user_id: The user's ID
            update_data: Fields to update
            
        Returns:
            Updated UserProfile
            
        Raises:
            ValueError: If user not found or email already taken
        """
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if update_data.name:
            update_doc["name"] = update_data.name
        
        if update_data.email:
            # Check if email is already taken
            existing = await self.collection.find_one({
                "email": update_data.email,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing:
                raise ValueError("Email already in use")
            update_doc["email"] = update_data.email
        
        # Update in database
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc}
            )
        except Exception:
            await self.collection.update_one(
                {"_id": user_id},
                {"$set": update_doc}
            )
        
        # Return updated profile
        return await self.get_profile(user_id)
    
    async def update_password(
        self,
        user_id: str,
        password_data: PasswordUpdate
    ) -> bool:
        """
        Update user password.
        
        Args:
            user_id: The user's ID
            password_data: Current and new password
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If current password is incorrect
        """
        # Get user
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = await self.collection.find_one({"_id": user_id})
        
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(
            password_data.current_password,
            user["hashed_password"]
        ):
            raise ValueError("Current password is incorrect")
        
        # Update password
        new_hash = get_password_hash(password_data.new_password)
        
        try:
            await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "hashed_password": new_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception:
            await self.collection.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "hashed_password": new_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        logger.info(f"Password updated for user: {user_id}")
        return True
    
    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access and refresh tokens
        """
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise ValueError("Invalid refresh token")
        
        # Generate new tokens
        new_access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
