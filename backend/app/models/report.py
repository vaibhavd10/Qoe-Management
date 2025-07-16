from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ReportType(str, enum.Enum):
    """Report type enumeration"""
    EXCEL_DATABOOK = "excel_databook"
    WORD_REPORT = "word_report"
    PDF_REPORT = "pdf_report"
    SUMMARY_REPORT = "summary_report"


class ReportStatus(str, enum.Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class Report(Base):
    """Report model for generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Report details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    
    # File information
    filename = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    
    # Generation status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Report configuration
    config = Column(JSON, nullable=True)  # Report-specific configuration
    template_used = Column(String, nullable=True)
    
    # QA checklist
    qa_checklist = Column(JSON, nullable=True)
    qa_completed = Column(Boolean, default=False)
    qa_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    generated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Generation metadata
    generation_time = Column(Integer, nullable=True)  # seconds
    adjustments_included = Column(Integer, default=0)
    
    # Relationships
    project = relationship("Project", back_populates="reports")
    generated_by_user = relationship("User", foreign_keys=[generated_by])
    qa_approved_by_user = relationship("User", foreign_keys=[qa_approved_by])
    
    def __repr__(self):
        return f"<Report {self.title}>"
    
    @property
    def is_completed(self) -> bool:
        """Check if report generation is completed"""
        return self.status == ReportStatus.COMPLETED
    
    @property
    def has_error(self) -> bool:
        """Check if report generation has error"""
        return self.status == ReportStatus.ERROR
    
    @property
    def is_ready_for_download(self) -> bool:
        """Check if report is ready for download"""
        return self.is_completed and self.qa_completed and self.file_path
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        if not self.file_size:
            return 0.0
        return self.file_size / (1024 * 1024)
    
    @property
    def file_extension(self) -> str:
        """Get file extension"""
        if not self.filename:
            return ""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ''