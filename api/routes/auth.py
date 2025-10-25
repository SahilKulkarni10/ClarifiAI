from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from models import UserCreate, UserLogin, User, Token
from auth import auth_manager, get_current_user, generate_user_id
from database import get_database
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Demo user for offline mode
DEMO_USER = {
    "user_id": "demo_user_123",
    "name": "Demo User",
    "email": "demo@financeai.com",
    "password": "$2b$12$LQv3c1yqBwLFBgn9fUz4hOUqIVSP8YNK.tVPr.9rWGFhEtJJ8n.Tm"  # "demo123"
}

@router.post("/demo-login", response_model=dict)
async def demo_login():
    """Demo login for offline mode"""
    try:
        # Create token for demo user
        access_token = auth_manager.create_token(DEMO_USER["user_id"], DEMO_USER["email"])
        
        logger.info("Demo user logged in (offline mode)")
        
        return {
            "message": "Demo login successful (offline mode)",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": DEMO_USER["user_id"],
                "name": DEMO_USER["name"],
                "email": DEMO_USER["email"]
            },
            "offline_mode": True
        }
        
    except Exception as e:
        logger.error(f"Demo login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        db = get_database()
        
        # Check if database is available
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable - running in offline mode"
            )
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = auth_manager.hash_password(user_data.password)
        
        # Create user
        user_id = generate_user_id()
        user_doc = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        
        # Create token
        access_token = auth_manager.create_token(user_id, user_data.email)
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user_id,
                "name": user_data.name,
                "email": user_data.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=dict)
async def login_user(user_data: UserLogin):
    """Login user"""
    try:
        db = get_database()
        
        # Check if database is available
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable - running in offline mode"
            )
        
        # Find user
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_manager.verify_password(user_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user_id (handle both user_id field and MongoDB's _id)
        user_id = user.get("user_id") or str(user["_id"])
        
        # Create token
        access_token = auth_manager.create_token(user_id, user["email"])
        
        logger.info(f"User logged in successfully: {user_data.email}")
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user_id,
                "name": user.get("name") or user.get("full_name", "User"),
                "email": user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/profile", response_model=dict)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    try:
        db = get_database()
        
        # Check if database is available
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable - running in offline mode"
            )
        
        # Find user (try both user_id and _id)
        user = await db.users.find_one(
            {"user_id": current_user["sub"]},
            {"password": 0}  # Exclude password
        )
        
        # If not found by user_id, try by _id
        if not user:
            try:
                from bson import ObjectId
                user = await db.users.find_one(
                    {"_id": ObjectId(current_user["sub"])},
                    {"password": 0}
                )
            except:
                pass
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user_id (handle both user_id field and MongoDB's _id)
        user_id = user.get("user_id") or str(user["_id"])
        
        return {
            "user": {
                "user_id": user_id,
                "name": user.get("name") or user.get("full_name", "User"),
                "email": user["email"],
                "created_at": user.get("created_at"),
                "is_active": user.get("is_active", True)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/status", response_model=dict)
async def get_auth_status():
    """Get authentication system status"""
    try:
        db = get_database()
        
        if db is None:
            return {
                "status": "offline",
                "database": "unavailable",
                "message": "Running in offline mode - use /auth/demo-login for testing"
            }
        
        # Test database connection
        await db.command("ping")
        
        return {
            "status": "online",
            "database": "connected",
            "message": "Authentication system fully operational"
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "status": "degraded",
            "database": "error",
            "message": f"Database connection issues: {str(e)}"
        }

@router.put("/profile", response_model=dict)
async def update_user_profile(
    name: str,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        db = get_database()
        
        # Update user
        result = await db.users.update_one(
            {"user_id": current_user["sub"]},
            {"$set": {"name": name, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Profile updated for user: {current_user['sub']}")
        
        return {"message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
