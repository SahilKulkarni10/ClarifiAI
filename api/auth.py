from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Token
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Truncate password to 72 bytes to comply with bcrypt limit
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Truncate password to 72 bytes to comply with bcrypt limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    return payload

def generate_user_id() -> str:
    """Generate unique user ID"""
    return str(uuid.uuid4())

class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return get_password_hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
    
    @staticmethod
    def create_token(user_id: str, email: str) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "email": email}, 
            expires_delta=access_token_expires
        )
        return access_token
    
    @staticmethod
    def verify_token(token: str) -> dict:
        return verify_token(token)

auth_manager = AuthManager()
