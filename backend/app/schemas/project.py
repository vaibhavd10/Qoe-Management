from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.project import ProjectStatus
from app.schemas.user import UserResponse


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    client_name: str = Field(..., min_length=1, max_length=200)
    materiality_threshold: float = Field(default=1000.0, ge=0)
    materiality_percentage: float = Field(default=0.03, ge=0, le=1)


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    materiality_threshold: Optional[float] = Field(None, ge=0)
    materiality_percentage: Optional[float] = Field(None, ge=0, le=1)
    status: Optional[ProjectStatus] = None
    qa_completed: Optional[bool] = None
    qa_notes: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    status: ProjectStatus
    owner_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metrics
    total_documents: int
    processed_documents: int
    total_adjustments: int
    reviewed_adjustments: int
    
    # QA
    qa_completed: bool
    qa_notes: Optional[str] = None
    
    # Computed properties
    completion_percentage: float
    adjustment_review_percentage: float
    is_ready_for_export: bool
    
    class Config:
        from_attributes = True


class ProjectWithRelations(ProjectResponse):
    """Project response with related data"""
    owner: UserResponse
    creator: UserResponse


class ProjectListResponse(BaseModel):
    """Project list response schema"""
    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ProjectDashboard(BaseModel):
    """Project dashboard schema"""
    id: int
    name: str
    client_name: str
    status: ProjectStatus
    completion_percentage: float
    adjustment_review_percentage: float
    total_documents: int
    processed_documents: int
    total_adjustments: int
    reviewed_adjustments: int
    qa_completed: bool
    is_ready_for_export: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProjectMetrics(BaseModel):
    """Project metrics schema"""
    total_projects: int
    active_projects: int
    completed_projects: int
    total_documents: int
    processed_documents: int
    total_adjustments: int
    reviewed_adjustments: int
    avg_completion_percentage: float
    avg_adjustment_review_percentage: float


class ProjectSettings(BaseModel):
    """Project settings schema"""
    materiality_threshold: float = Field(..., ge=0)
    materiality_percentage: float = Field(..., ge=0, le=1)
    
    class Config:
        from_attributes = True