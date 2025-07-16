from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AdjustmentType(str, enum.Enum):
    """Adjustment type enumeration"""
    REVENUE_RECOGNITION = "revenue_recognition"
    EXPENSE_ACCRUAL = "expense_accrual"
    DEPRECIATION = "depreciation"
    INVENTORY_VALUATION = "inventory_valuation"
    BAD_DEBT = "bad_debt"
    PREPAID_EXPENSES = "prepaid_expenses"
    ACCRUED_LIABILITIES = "accrued_liabilities"
    PAYROLL_ACCRUAL = "payroll_accrual"
    RENT_ADJUSTMENT = "rent_adjustment"
    INSURANCE_ADJUSTMENT = "insurance_adjustment"
    TAX_ADJUSTMENT = "tax_adjustment"
    INTERCOMPANY_ELIMINATION = "intercompany_elimination"
    RECLASSIFICATION = "reclassification"
    WRITE_OFF = "write_off"
    BONUS_ACCRUAL = "bonus_accrual"
    COMMISSION_ACCRUAL = "commission_accrual"
    PROFESSIONAL_FEES = "professional_fees"
    LITIGATION_RESERVE = "litigation_reserve"
    WARRANTY_RESERVE = "warranty_reserve"
    STOCK_COMPENSATION = "stock_compensation"
    GOODWILL_IMPAIRMENT = "goodwill_impairment"
    ASSET_IMPAIRMENT = "asset_impairment"
    LEASE_ADJUSTMENT = "lease_adjustment"
    PENSION_ADJUSTMENT = "pension_adjustment"
    FOREIGN_EXCHANGE = "foreign_exchange"
    RESTRUCTURING = "restructuring"
    ACQUISITION_ADJUSTMENT = "acquisition_adjustment"
    OTHER = "other"


class AdjustmentStatus(str, enum.Enum):
    """Adjustment review status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"


class Adjustment(Base):
    """Adjustment model for financial adjustments"""
    __tablename__ = "adjustments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Adjustment details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    adjustment_type = Column(Enum(AdjustmentType), nullable=False)
    
    # Financial impact
    amount = Column(Float, nullable=False)
    debit_account = Column(String, nullable=True)
    credit_account = Column(String, nullable=True)
    account_impact = Column(JSON, nullable=True)  # Detailed account impacts
    
    # AI-generated content
    narrative = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    rule_applied = Column(String, nullable=True)
    
    # Review status
    status = Column(Enum(AdjustmentStatus), default=AdjustmentStatus.PENDING, nullable=False)
    reviewer_notes = Column(Text, nullable=True)
    
    # Materiality assessment
    is_material = Column(Boolean, default=False)
    materiality_reason = Column(Text, nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    source_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing metadata
    processing_time = Column(Integer, nullable=True)  # milliseconds
    ai_model_used = Column(String, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="adjustments")
    source_document = relationship("Document", back_populates="adjustments")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="adjustments")
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<Adjustment {self.title}>"
    
    @property
    def is_accepted(self) -> bool:
        """Check if adjustment is accepted"""
        return self.status == AdjustmentStatus.ACCEPTED
    
    @property
    def is_rejected(self) -> bool:
        """Check if adjustment is rejected"""
        return self.status == AdjustmentStatus.REJECTED
    
    @property
    def is_modified(self) -> bool:
        """Check if adjustment is modified"""
        return self.status == AdjustmentStatus.MODIFIED
    
    @property
    def is_pending(self) -> bool:
        """Check if adjustment is pending review"""
        return self.status == AdjustmentStatus.PENDING
    
    @property
    def absolute_amount(self) -> float:
        """Get absolute value of adjustment amount"""
        return abs(self.amount)
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if adjustment has high confidence score"""
        return self.confidence_score >= 0.8
    
    @property
    def confidence_percentage(self) -> int:
        """Get confidence score as percentage"""
        return int(self.confidence_score * 100)