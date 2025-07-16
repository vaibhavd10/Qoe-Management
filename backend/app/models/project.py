from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class Project(Base):
    """Project model for managing QoE analysis projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    client_name = Column(String, nullable=False)
    
    # Project settings
    materiality_threshold = Column(Float, default=1000.0)
    materiality_percentage = Column(Float, default=0.03)  # 3%
    
    # Status and ownership
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Project metrics
    total_documents = Column(Integer, default=0)
    processed_documents = Column(Integer, default=0)
    total_adjustments = Column(Integer, default=0)
    reviewed_adjustments = Column(Integer, default=0)
    
    # QA checklist
    qa_completed = Column(Boolean, default=False)
    qa_notes = Column(Text, nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="projects")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    adjustments = relationship("Adjustment", back_populates="project", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.name}>"
    
    @property
    def completion_percentage(self) -> float:
        """Calculate project completion percentage"""
        if self.total_documents == 0:
            return 0.0
        return (self.processed_documents / self.total_documents) * 100
    
    @property
    def adjustment_review_percentage(self) -> float:
        """Calculate adjustment review percentage"""
        if self.total_adjustments == 0:
            return 0.0
        return (self.reviewed_adjustments / self.total_adjustments) * 100
    
    @property
    def is_ready_for_export(self) -> bool:
        """Check if project is ready for report export"""
        return (
            self.processed_documents == self.total_documents and
            self.reviewed_adjustments == self.total_adjustments and
            self.qa_completed
        )