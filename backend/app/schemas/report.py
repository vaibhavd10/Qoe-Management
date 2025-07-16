from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.report import ReportType, ReportStatus
from app.schemas.user import UserResponse


class ReportBase(BaseModel):
    """Base report schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    report_type: ReportType
    config: Optional[Dict[str, Any]] = None
    template_used: Optional[str] = None


class ReportCreate(ReportBase):
    """Report creation schema"""
    project_id: int
    qa_checklist: Optional[Dict[str, Any]] = None


class ReportUpdate(BaseModel):
    """Report update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ReportStatus] = None
    error_message: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    template_used: Optional[str] = None
    qa_checklist: Optional[Dict[str, Any]] = None
    qa_completed: Optional[bool] = None


class ReportResponse(ReportBase):
    """Report response schema"""
    id: int
    project_id: int
    generated_by: int
    
    # File information
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    # Status
    status: ReportStatus
    error_message: Optional[str] = None
    
    # QA
    qa_checklist: Optional[Dict[str, Any]] = None
    qa_completed: bool
    qa_approved_by: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    generated_at: Optional[datetime] = None
    
    # Metadata
    generation_time: Optional[int] = None
    adjustments_included: int
    
    # Computed properties
    is_completed: bool
    has_error: bool
    is_ready_for_download: bool
    file_size_mb: float
    file_extension: str
    
    class Config:
        from_attributes = True


class ReportWithRelations(ReportResponse):
    """Report response with related data"""
    generated_by_user: UserResponse
    qa_approved_by_user: Optional[UserResponse] = None


class ReportListResponse(BaseModel):
    """Report list response schema"""
    reports: List[ReportResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ReportGeneration(BaseModel):
    """Report generation schema"""
    project_id: int
    report_type: ReportType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    template_used: Optional[str] = None
    include_rejected_adjustments: bool = False
    include_pending_adjustments: bool = True


class ReportQAChecklist(BaseModel):
    """Report QA checklist schema"""
    financial_accuracy: bool = False
    adjustment_completeness: bool = False
    narrative_quality: bool = False
    format_compliance: bool = False
    data_consistency: bool = False
    client_requirements: bool = False
    regulatory_compliance: bool = False
    notes: Optional[str] = None


class ReportQAUpdate(BaseModel):
    """Report QA update schema"""
    qa_checklist: ReportQAChecklist
    qa_completed: bool
    qa_notes: Optional[str] = None


class ReportMetrics(BaseModel):
    """Report metrics schema"""
    total_reports: int
    pending_reports: int
    generating_reports: int
    completed_reports: int
    error_reports: int
    
    # By type
    by_type: Dict[ReportType, int]
    
    # By status
    by_status: Dict[ReportStatus, int]
    
    # QA metrics
    qa_completed_reports: int
    qa_pending_reports: int
    
    # Generation stats
    avg_generation_time: float
    total_file_size: int
    
    class Config:
        from_attributes = True


class ReportSummary(BaseModel):
    """Report summary schema"""
    id: int
    title: str
    report_type: ReportType
    status: ReportStatus
    qa_completed: bool
    file_size_mb: float
    generated_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportTemplate(BaseModel):
    """Report template schema"""
    name: str
    report_type: ReportType
    description: Optional[str] = None
    config: Dict[str, Any]
    is_default: bool = False


class ReportDownload(BaseModel):
    """Report download schema"""
    filename: str
    file_path: str
    file_size: int
    content_type: str
    
    class Config:
        from_attributes = True


class ReportExport(BaseModel):
    """Report export schema"""
    project_id: int
    report_ids: List[int]
    format: str = Field(..., pattern="^(zip|tar)$")
    include_source_data: bool = False