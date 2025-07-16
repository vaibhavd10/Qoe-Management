from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from app.models.question import QuestionType, QuestionPriority, QuestionStatus
from app.schemas.user import UserResponse


class QuestionBase(BaseModel):
    """Base question schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    question_type: QuestionType = QuestionType.TEXT
    options: Optional[List[str]] = None
    priority: QuestionPriority = QuestionPriority.MEDIUM


class QuestionCreate(QuestionBase):
    """Question creation schema"""
    project_id: int
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    depends_on_question_id: Optional[int] = None
    depends_on_answer: Optional[str] = None
    is_ai_generated: bool = False
    ai_context: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class QuestionUpdate(BaseModel):
    """Question update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    priority: Optional[QuestionPriority] = None
    status: Optional[QuestionStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    depends_on_question_id: Optional[int] = None
    depends_on_answer: Optional[str] = None


class QuestionResponse(QuestionBase):
    """Question response schema"""
    id: int
    project_id: int
    assigned_to: Optional[int] = None
    created_by: int
    
    # Status
    status: QuestionStatus
    
    # AI metadata
    is_ai_generated: bool
    ai_context: Optional[str] = None
    confidence_score: float
    
    # Conditional logic
    depends_on_question_id: Optional[int] = None
    depends_on_answer: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    # Computed properties
    is_answered: bool
    is_overdue: bool
    
    class Config:
        from_attributes = True


class QuestionWithRelations(QuestionResponse):
    """Question response with related data"""
    assigned_to_user: Optional[UserResponse] = None
    created_by_user: UserResponse
    depends_on_question: Optional['QuestionResponse'] = None
    answers: List['AnswerResponse'] = []


class QuestionListResponse(BaseModel):
    """Question list response schema"""
    questions: List[QuestionResponse]
    total: int
    page: int
    per_page: int
    pages: int


class AnswerBase(BaseModel):
    """Base answer schema"""
    answer_text: Optional[str] = None
    answer_number: Optional[float] = None
    answer_date: Optional[datetime] = None
    answer_boolean: Optional[bool] = None
    answer_file_path: Optional[str] = None
    notes: Optional[str] = None
    is_final: bool = False


class AnswerCreate(AnswerBase):
    """Answer creation schema"""
    question_id: int


class AnswerUpdate(BaseModel):
    """Answer update schema"""
    answer_text: Optional[str] = None
    answer_number: Optional[float] = None
    answer_date: Optional[datetime] = None
    answer_boolean: Optional[bool] = None
    answer_file_path: Optional[str] = None
    notes: Optional[str] = None
    is_final: Optional[bool] = None


class AnswerResponse(AnswerBase):
    """Answer response schema"""
    id: int
    question_id: int
    answered_by: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed properties
    answer_value: Union[str, float, datetime, bool, None]
    
    class Config:
        from_attributes = True


class AnswerWithRelations(AnswerResponse):
    """Answer response with related data"""
    answered_by_user: UserResponse
    question: QuestionResponse


class AnswerListResponse(BaseModel):
    """Answer list response schema"""
    answers: List[AnswerResponse]
    total: int
    page: int
    per_page: int
    pages: int


class QuestionMetrics(BaseModel):
    """Question metrics schema"""
    total_questions: int
    pending_questions: int
    answered_questions: int
    overdue_questions: int
    
    # By type
    by_type: Dict[QuestionType, int]
    
    # By priority
    by_priority: Dict[QuestionPriority, int]
    
    # By status
    by_status: Dict[QuestionStatus, int]
    
    # AI metrics
    ai_generated_questions: int
    avg_confidence_score: float
    
    # Response stats
    avg_response_time: float
    
    class Config:
        from_attributes = True


class QuestionSummary(BaseModel):
    """Question summary schema"""
    id: int
    title: str
    question_type: QuestionType
    priority: QuestionPriority
    status: QuestionStatus
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    is_overdue: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionnaireGeneration(BaseModel):
    """Questionnaire generation schema"""
    project_id: int
    document_types: List[str] = []
    adjustment_types: List[str] = []
    ai_prompt: Optional[str] = None
    max_questions: int = Field(default=20, ge=1, le=100)


class QuestionnaireResponse(BaseModel):
    """Questionnaire response schema"""
    project_id: int
    questions: List[QuestionResponse]
    total_questions: int
    ai_generated: int
    manual_questions: int
    
    class Config:
        from_attributes = True


# Forward reference resolution
QuestionWithRelations.model_rebuild()