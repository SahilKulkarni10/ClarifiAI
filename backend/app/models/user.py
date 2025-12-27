"""
User Models
Pydantic models for user-related data structures.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Model for user registration request."""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Model for user login request."""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Model representing a user document in MongoDB."""
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """Model for user data in API responses."""
    id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        populate_by_name = True


class UserProfile(BaseModel):
    """Model for user profile response."""
    id: str
    email: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[str] = None
    preferences: Optional[dict] = {}


class UserProfileUpdate(BaseModel):
    """Model for updating user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class PasswordUpdate(BaseModel):
    """Model for password update request."""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class AuthResponse(BaseModel):
    """Model for authentication response with tokens."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    """Model for token refresh request."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Model for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
