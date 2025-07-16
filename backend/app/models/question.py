from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class QuestionType(str, enum.Enum):
    """Question type enumeration"""
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    NUMBER = "number"
    DATE = "date"
    FILE_UPLOAD = "file_upload"


class QuestionPriority(str, enum.Enum):
    """Question priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QuestionStatus(str, enum.Enum):
    """Question status enumeration"""
    PENDING = "pending"
    ANSWERED = "answered"
    CLARIFICATION_NEEDED = "clarification_needed"
    CLOSED = "closed"


class Question(Base):
    """Question model for questionnaire system"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Question content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.TEXT, nullable=False)
    
    # Question options (for multiple choice)
    options = Column(JSON, nullable=True)  # List of options for multiple choice
    
    # Question metadata
    priority = Column(Enum(QuestionPriority), default=QuestionPriority.MEDIUM, nullable=False)
    status = Column(Enum(QuestionStatus), default=QuestionStatus.PENDING, nullable=False)
    
    # AI-generated metadata
    is_ai_generated = Column(Boolean, default=False)
    ai_context = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Conditional logic
    depends_on_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    depends_on_answer = Column(String, nullable=True)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="questions")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to], back_populates="questions")
    created_by_user = relationship("User", foreign_keys=[created_by])
    depends_on_question = relationship("Question", remote_side=[id])
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question {self.title}>"
    
    @property
    def is_answered(self) -> bool:
        """Check if question is answered"""
        return self.status == QuestionStatus.ANSWERED
    
    @property
    def is_overdue(self) -> bool:
        """Check if question is overdue"""
        if not self.due_date:
            return False
        return self.due_date < func.now() and not self.is_answered
    
    @property
    def latest_answer(self):
        """Get the latest answer to this question"""
        return max(self.answers, key=lambda x: x.created_at, default=None)


class Answer(Base):
    """Answer model for questionnaire responses"""
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Answer content
    answer_text = Column(Text, nullable=True)
    answer_number = Column(Float, nullable=True)
    answer_date = Column(DateTime(timezone=True), nullable=True)
    answer_boolean = Column(Boolean, nullable=True)
    answer_file_path = Column(String, nullable=True)
    
    # Answer metadata
    is_final = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    answered_by_user = relationship("User", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer to {self.question.title}>"
    
    @property
    def answer_value(self):
        """Get the appropriate answer value based on question type"""
        if self.question.question_type == QuestionType.TEXT:
            return self.answer_text
        elif self.question.question_type == QuestionType.NUMBER:
            return self.answer_number
        elif self.question.question_type == QuestionType.DATE:
            return self.answer_date
        elif self.question.question_type == QuestionType.YES_NO:
            return self.answer_boolean
        elif self.question.question_type == QuestionType.FILE_UPLOAD:
            return self.answer_file_path
        else:
            return self.answer_text