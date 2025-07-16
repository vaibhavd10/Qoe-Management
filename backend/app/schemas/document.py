from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.document import DocumentStatus, DocumentType
from app.schemas.user import UserResponse


class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    document_type: DocumentType = DocumentType.OTHER


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    project_id: int


class DocumentUpdate(BaseModel):
    """Document update schema"""
    document_type: Optional[DocumentType] = None
    classification_confidence: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None
    processing_notes: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Document response schema"""
    id: int
    project_id: int
    uploaded_by: int
    
    # Classification
    document_type: DocumentType
    classification_confidence: int
    
    # Status
    status: DocumentStatus
    error_message: Optional[str] = None
    
    # Data
    extracted_data: Optional[Dict[str, Any]] = None
    row_count: int
    column_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Processing
    processing_time: Optional[int] = None
    processing_notes: Optional[str] = None
    
    # Computed properties
    file_extension: str
    is_excel: bool
    is_csv: bool
    is_pdf: bool
    is_word: bool
    is_processed: bool
    has_error: bool
    
    class Config:
        from_attributes = True


class DocumentWithRelations(DocumentResponse):
    """Document response with related data"""
    uploaded_by_user: UserResponse


class DocumentListResponse(BaseModel):
    """Document list response schema"""
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class DocumentUploadResponse(BaseModel):
    """Document upload response schema"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    status: DocumentStatus
    message: str


class DocumentProcessingStatus(BaseModel):
    """Document processing status schema"""
    id: int
    filename: str
    status: DocumentStatus
    progress: int = Field(..., ge=0, le=100)
    error_message: Optional[str] = None
    processing_time: Optional[int] = None
    
    class Config:
        from_attributes = True


class DocumentPreview(BaseModel):
    """Document preview schema"""
    id: int
    filename: str
    document_type: DocumentType
    row_count: int
    column_count: int
    sample_data: Optional[List[Dict[str, Any]]] = None
    headers: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class DocumentClassification(BaseModel):
    """Document classification schema"""
    document_type: DocumentType
    confidence: int = Field(..., ge=0, le=100)
    reasons: List[str] = []


class DocumentMetrics(BaseModel):
    """Document metrics schema"""
    total_documents: int
    pending_documents: int
    processing_documents: int
    completed_documents: int
    error_documents: int
    
    # By type
    by_type: Dict[DocumentType, int]
    
    # By status
    by_status: Dict[DocumentStatus, int]
    
    # Processing stats
    avg_processing_time: float
    total_file_size: int
    
    class Config:
        from_attributes = True