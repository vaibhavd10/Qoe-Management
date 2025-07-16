from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import UserResponse

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    full_name: str
    password: str
    role: Optional[str] = "analyst"

class RefreshToken(BaseModel):
    """Refresh token schema"""
    refresh_token: str