from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, BigInteger, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class DocumentType(str, enum.Enum):
    """Document type classification"""
    GENERAL_LEDGER = "general_ledger"
    PROFIT_LOSS = "profit_loss"
    BALANCE_SHEET = "balance_sheet"
    TRIAL_BALANCE = "trial_balance"
    PAYROLL = "payroll"
    CASH_FLOW = "cash_flow"
    SUPPORTING_DOCS = "supporting_docs"
    OTHER = "other"


class Document(Base):
    """Document model for file management and processing"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Document classification
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER, nullable=False)
    classification_confidence = Column(Integer, default=0)  # 0-100
    
    # Processing status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Extracted data
    extracted_data = Column(JSON, nullable=True)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing metadata
    processing_time = Column(Integer, nullable=True)  # seconds
    processing_notes = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    uploaded_by_user = relationship("User", back_populates="documents")
    adjustments = relationship("Adjustment", back_populates="source_document")
    
    def __repr__(self):
        return f"<Document {self.original_filename}>"
    
    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return self.original_filename.split('.')[-1].lower() if '.' in self.original_filename else ''
    
    @property
    def is_excel(self) -> bool:
        """Check if document is Excel file"""
        return self.file_extension in ['xlsx', 'xls']
    
    @property
    def is_csv(self) -> bool:
        """Check if document is CSV file"""
        return self.file_extension == 'csv'
    
    @property
    def is_pdf(self) -> bool:
        """Check if document is PDF file"""
        return self.file_extension == 'pdf'
    
    @property
    def is_word(self) -> bool:
        """Check if document is Word file"""
        return self.file_extension in ['docx', 'doc']
    
    @property
    def is_processed(self) -> bool:
        """Check if document is processed"""
        return self.status == DocumentStatus.COMPLETED
    
    @property
    def has_error(self) -> bool:
        """Check if document has processing error"""
        return self.status == DocumentStatus.ERROR