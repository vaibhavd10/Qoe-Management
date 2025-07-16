from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    ANALYST = "analyst"


class User(Base):
    """User model for authentication and role management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ANALYST, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    created_projects = relationship("Project", foreign_keys="Project.created_by", back_populates="creator")
    documents = relationship("Document", back_populates="uploaded_by_user")
    adjustments = relationship("Adjustment", back_populates="created_by_user")
    questions = relationship("Question", back_populates="assigned_to_user")
    answers = relationship("Answer", back_populates="answered_by_user")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_analyst(self) -> bool:
        """Check if user is analyst"""
        return self.role == UserRole.ANALYST