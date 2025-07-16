from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.adjustment import AdjustmentType, AdjustmentStatus
from app.schemas.user import UserResponse
from app.schemas.document import DocumentResponse


class AdjustmentBase(BaseModel):
    """Base adjustment schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    adjustment_type: AdjustmentType
    amount: float
    debit_account: Optional[str] = None
    credit_account: Optional[str] = None
    account_impact: Optional[Dict[str, Any]] = None


class AdjustmentCreate(AdjustmentBase):
    """Adjustment creation schema"""
    project_id: int
    source_document_id: Optional[int] = None
    narrative: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    rule_applied: Optional[str] = None


class AdjustmentUpdate(BaseModel):
    """Adjustment update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    adjustment_type: Optional[AdjustmentType] = None
    amount: Optional[float] = None
    debit_account: Optional[str] = None
    credit_account: Optional[str] = None
    account_impact: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None
    status: Optional[AdjustmentStatus] = None
    reviewer_notes: Optional[str] = None
    is_material: Optional[bool] = None
    materiality_reason: Optional[str] = None


class AdjustmentResponse(AdjustmentBase):
    """Adjustment response schema"""
    id: int
    project_id: int
    source_document_id: Optional[int] = None
    created_by: int
    reviewed_by: Optional[int] = None
    
    # AI content
    narrative: Optional[str] = None
    confidence_score: float
    rule_applied: Optional[str] = None
    
    # Review
    status: AdjustmentStatus
    reviewer_notes: Optional[str] = None
    
    # Materiality
    is_material: bool
    materiality_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    
    # Processing
    processing_time: Optional[int] = None
    ai_model_used: Optional[str] = None
    
    # Computed properties
    is_accepted: bool
    is_rejected: bool
    is_modified: bool
    is_pending: bool
    absolute_amount: float
    is_high_confidence: bool
    confidence_percentage: int
    
    class Config:
        from_attributes = True


class AdjustmentWithRelations(AdjustmentResponse):
    """Adjustment response with related data"""
    created_by_user: UserResponse
    reviewed_by_user: Optional[UserResponse] = None
    source_document: Optional[DocumentResponse] = None


class AdjustmentListResponse(BaseModel):
    """Adjustment list response schema"""
    adjustments: List[AdjustmentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class AdjustmentReview(BaseModel):
    """Adjustment review schema"""
    status: AdjustmentStatus
    reviewer_notes: Optional[str] = None
    
    # For modifications
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    amount: Optional[float] = None
    debit_account: Optional[str] = None
    credit_account: Optional[str] = None
    account_impact: Optional[Dict[str, Any]] = None


class AdjustmentMetrics(BaseModel):
    """Adjustment metrics schema"""
    total_adjustments: int
    pending_adjustments: int
    accepted_adjustments: int
    rejected_adjustments: int
    modified_adjustments: int
    
    # By type
    by_type: Dict[AdjustmentType, int]
    
    # By status
    by_status: Dict[AdjustmentStatus, int]
    
    # Material vs non-material
    material_adjustments: int
    non_material_adjustments: int
    
    # Financial impact
    total_adjustment_amount: float
    avg_adjustment_amount: float
    
    # AI metrics
    avg_confidence_score: float
    high_confidence_adjustments: int
    
    # Processing stats
    avg_processing_time: float
    
    class Config:
        from_attributes = True


class AdjustmentSummary(BaseModel):
    """Adjustment summary schema"""
    id: int
    title: str
    adjustment_type: AdjustmentType
    amount: float
    status: AdjustmentStatus
    confidence_score: float
    is_material: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdjustmentBulkAction(BaseModel):
    """Adjustment bulk action schema"""
    adjustment_ids: List[int]
    action: AdjustmentStatus
    reviewer_notes: Optional[str] = None


class AdjustmentExport(BaseModel):
    """Adjustment export schema"""
    project_id: int
    format: str = Field(..., pattern="^(excel|csv|pdf)$")
    include_rejected: bool = False
    include_pending: bool = True