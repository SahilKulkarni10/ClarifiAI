"""
Authentication Dependencies
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_access_token
from app.core.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate the current user ID from the JWT token.
    
    Args:
        credentials: Bearer token credentials from the request
        
    Returns:
        The user ID from the token
        
    Raises:
        HTTPException: If token is missing, invalid, or user_id not found
    """
    token = credentials.credentials
    payload = verify_access_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> dict:
    """
    Get the current authenticated user from the database.
    
    Args:
        user_id: The user ID extracted from the JWT token
        db: MongoDB database instance
        
    Returns:
        User document from the database
        
    Raises:
        HTTPException: If user not found in database
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        # Handle case where user_id is not a valid ObjectId
        user = await db.users.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Convert ObjectId to string for JSON serialization
    user["_id"] = str(user["_id"])
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Optional[dict]:
    """
    Optionally get the current user if authenticated.
    Returns None if no valid token is provided.
    
    Args:
        credentials: Optional bearer token credentials
        db: MongoDB database instance
        
    Returns:
        User document if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = await db.users.find_one({"_id": user_id})
        
        if user:
            user["_id"] = str(user["_id"])
            return user
        
        return None
        
    except Exception:
        return None
