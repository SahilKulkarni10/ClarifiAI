"""
Authentication Routes
Handles user registration, login, profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.core.database import get_database
from app.core.dependencies import get_current_user
from app.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserProfile,
    AuthResponse,
    PasswordUpdate,
    TokenRefresh,
    UserProfileUpdate
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user.
    
    - Creates user account with hashed password
    - Returns access and refresh tokens
    """
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.register(user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Authenticate user and return tokens.
    
    - Validates email and password
    - Returns access and refresh tokens
    """
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.login(credentials)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's profile.
    
    Requires authentication via Bearer token.
    """
    return UserProfile(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        phone=current_user.get("phone"),
        created_at=current_user.get("created_at", ""),
        preferences=current_user.get("preferences", {})
    )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update current user's profile.
    
    - Can update name, phone, and preferences
    """
    auth_service = AuthService(db)
    
    try:
        updated_user = await auth_service.update_profile(
            user_id=str(current_user["_id"]),
            update_data=profile_data
        )
        
        return UserProfile(
            id=str(updated_user["_id"]),
            email=updated_user["email"],
            full_name=updated_user.get("full_name"),
            phone=updated_user.get("phone"),
            created_at=updated_user.get("created_at", ""),
            preferences=updated_user.get("preferences", {})
        )
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/profile/password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update current user's password.
    
    - Requires current password for verification
    - Sets new password
    """
    auth_service = AuthService(db)
    
    try:
        success = await auth_service.update_password(
            user_id=str(current_user["_id"]),
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_tokens(
    refresh_data: TokenRefresh,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Refresh access token using refresh token.
    
    - Validates refresh token
    - Returns new access and refresh tokens
    """
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.refresh_tokens(refresh_data.refresh_token)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: With JWT, the client should discard the token.
    This endpoint can be used for audit logging.
    """
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Logged out successfully"}
