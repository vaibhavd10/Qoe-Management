from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
from fastapi import HTTPException, status

from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.config import settings


class ProjectService:
    """Service for handling project operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Project]:
        """Get all projects with pagination and optional user filtering"""
        query = self.db.query(Project)
        
        if user_id:
            # For non-admin users, only show projects they own or are assigned to
            query = query.filter(
                or_(
                    Project.owner_id == user_id,
                    Project.created_by == user_id
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(self, user_id: Optional[int] = None) -> int:
        """Get total project count"""
        query = self.db.query(Project)
        
        if user_id:
            query = query.filter(
                or_(
                    Project.owner_id == user_id,
                    Project.created_by == user_id
                )
            )
        
        return query.count()
    
    def create(self, project_data: ProjectCreate, user_id: int) -> Project:
        """Create new project"""
        project = Project(
            name=project_data.name,
            description=project_data.description,
            client_name=project_data.client_name,
            materiality_threshold=project_data.materiality_threshold,
            materiality_percentage=project_data.materiality_percentage,
            owner_id=user_id,
            created_by=user_id,
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def update(self, project_id: int, project_data: ProjectUpdate, user_id: int) -> Project:
        """Update project"""
        project = self.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check permissions
        if not self._can_modify_project(project, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this project"
            )
        
        # Update fields
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)
        
        # Mark as completed if status changes to completed
        if project_data.status == ProjectStatus.COMPLETED:
            project.completed_at = datetime.utcnow()
        
        project.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def delete(self, project_id: int, user_id: int) -> bool:
        """Delete project"""
        project = self.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check permissions
        if not self._can_modify_project(project, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project"
            )
        
        self.db.delete(project)
        self.db.commit()
        
        return True
    
    def get_by_status(self, status: ProjectStatus, user_id: Optional[int] = None) -> List[Project]:
        """Get projects by status"""
        query = self.db.query(Project).filter(Project.status == status)
        
        if user_id:
            query = query.filter(
                or_(
                    Project.owner_id == user_id,
                    Project.created_by == user_id
                )
            )
        
        return query.all()
    
    def get_active_projects(self, user_id: Optional[int] = None) -> List[Project]:
        """Get active projects"""
        return self.get_by_status(ProjectStatus.ACTIVE, user_id)
    
    def get_completed_projects(self, user_id: Optional[int] = None) -> List[Project]:
        """Get completed projects"""
        return self.get_by_status(ProjectStatus.COMPLETED, user_id)
    
    def get_dashboard_data(self, user_id: Optional[int] = None) -> dict:
        """Get dashboard data for projects"""
        query = self.db.query(Project)
        
        if user_id:
            query = query.filter(
                or_(
                    Project.owner_id == user_id,
                    Project.created_by == user_id
                )
            )
        
        projects = query.all()
        
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.status == ProjectStatus.ACTIVE)
        completed_projects = sum(1 for p in projects if p.status == ProjectStatus.COMPLETED)
        
        total_documents = sum(p.total_documents for p in projects)
        processed_documents = sum(p.processed_documents for p in projects)
        
        total_adjustments = sum(p.total_adjustments for p in projects)
        reviewed_adjustments = sum(p.reviewed_adjustments for p in projects)
        
        avg_completion = 0
        avg_adjustment_review = 0
        
        if total_projects > 0:
            avg_completion = sum(p.completion_percentage for p in projects) / total_projects
            avg_adjustment_review = sum(p.adjustment_review_percentage for p in projects) / total_projects
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "total_adjustments": total_adjustments,
            "reviewed_adjustments": reviewed_adjustments,
            "avg_completion_percentage": avg_completion,
            "avg_adjustment_review_percentage": avg_adjustment_review,
        }
    
    def update_metrics(self, project_id: int) -> Project:
        """Update project metrics based on related data"""
        project = self.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Update document counts
        project.total_documents = len(project.documents)
        project.processed_documents = sum(
            1 for doc in project.documents if doc.is_processed
        )
        
        # Update adjustment counts
        project.total_adjustments = len(project.adjustments)
        project.reviewed_adjustments = sum(
            1 for adj in project.adjustments if not adj.is_pending
        )
        
        project.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def check_materiality(self, project_id: int, amount: float) -> bool:
        """Check if an amount is material for a project"""
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        # Check against absolute threshold
        if abs(amount) >= project.materiality_threshold:
            return True
        
        # Check against percentage threshold (would need EBITDA calculation)
        # For now, just use threshold
        return False
    
    def _can_modify_project(self, project: Project, user_id: int) -> bool:
        """Check if user can modify project"""
        # Get user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Admin can modify any project
        if user.role == UserRole.ADMIN:
            return True
        
        # Owner can modify their project
        if project.owner_id == user_id:
            return True
        
        # Creator can modify their project
        if project.created_by == user_id:
            return True
        
        return False
    
    def get_recent_projects(self, user_id: Optional[int] = None, limit: int = 5) -> List[Project]:
        """Get recent projects"""
        query = self.db.query(Project)
        
        if user_id:
            query = query.filter(
                or_(
                    Project.owner_id == user_id,
                    Project.created_by == user_id
                )
            )
        
        return query.order_by(Project.updated_at.desc()).limit(limit).all()
    
    def search_projects(self, query: str, user_id: Optional[int] = None) -> List[Project]:
        """Search projects by name or client name"""
        db_query = self.db.query(Project).filter(
            or_(
                Project.name.ilike(f"%{query}%"),
                Project.client_name.ilike(f"%{query}%")
            )
        )
        
        if user_id:
            db_query = db_query.filter(
                or_(
                    Project.owner_id == user_id,
                    Project.created_by == user_id
                )
            )
        
        return db_query.all()