from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user, get_admin_user
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectDashboard, ProjectMetrics, ProjectSettings
)
from app.services.project import ProjectService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects with pagination"""
    project_service = ProjectService(db)
    
    # For non-admin users, filter by user
    user_id = None if current_user.is_admin else current_user.id
    
    projects = project_service.get_all(skip=skip, limit=limit, user_id=user_id)
    total = project_service.get_count(user_id=user_id)
    
    pages = (total + limit - 1) // limit
    
    return ProjectListResponse(
        projects=[ProjectResponse.from_orm(p) for p in projects],
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        pages=pages
    )


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project_service = ProjectService(db)
    project = project_service.create(project_data, current_user.id)
    return ProjectResponse.from_orm(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project_service = ProjectService(db)
    project = project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if not current_user.is_admin and project.owner_id != current_user.id and project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    return ProjectResponse.from_orm(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project_service = ProjectService(db)
    project = project_service.update(project_id, project_data, current_user.id)
    return ProjectResponse.from_orm(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project_service = ProjectService(db)
    project_service.delete(project_id, current_user.id)
    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/dashboard", response_model=ProjectDashboard)
async def get_project_dashboard(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project dashboard data"""
    project_service = ProjectService(db)
    project = project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if not current_user.is_admin and project.owner_id != current_user.id and project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    return ProjectDashboard.from_orm(project)


@router.get("/{project_id}/metrics", response_model=ProjectMetrics)
async def get_project_metrics(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project metrics"""
    project_service = ProjectService(db)
    project = project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if not current_user.is_admin and project.owner_id != current_user.id and project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    # Calculate metrics
    metrics = {
        "total_projects": 1,
        "active_projects": 1 if project.status == "active" else 0,
        "completed_projects": 1 if project.status == "completed" else 0,
        "total_documents": project.total_documents,
        "processed_documents": project.processed_documents,
        "total_adjustments": project.total_adjustments,
        "reviewed_adjustments": project.reviewed_adjustments,
        "avg_completion_percentage": project.completion_percentage,
        "avg_adjustment_review_percentage": project.adjustment_review_percentage
    }
    
    return ProjectMetrics(**metrics)


@router.put("/{project_id}/settings", response_model=ProjectSettings)
async def update_project_settings(
    project_id: int,
    settings_data: ProjectSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project settings"""
    project_service = ProjectService(db)
    project = project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if not current_user.is_admin and project.owner_id != current_user.id and project.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project"
        )
    
    # Update settings
    project.materiality_threshold = settings_data.materiality_threshold
    project.materiality_percentage = settings_data.materiality_percentage
    
    db.commit()
    db.refresh(project)
    
    return ProjectSettings.from_orm(project)


@router.post("/{project_id}/update-metrics")
async def update_project_metrics(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually update project metrics"""
    project_service = ProjectService(db)
    project = project_service.update_metrics(project_id)
    return {"message": "Project metrics updated successfully"}


@router.get("/dashboard/overview", response_model=ProjectMetrics)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard overview for all projects"""
    project_service = ProjectService(db)
    
    # For non-admin users, filter by user
    user_id = None if current_user.is_admin else current_user.id
    
    dashboard_data = project_service.get_dashboard_data(user_id=user_id)
    return ProjectMetrics(**dashboard_data)


@router.get("/recent", response_model=List[ProjectResponse])
async def get_recent_projects(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent projects"""
    project_service = ProjectService(db)
    
    # For non-admin users, filter by user
    user_id = None if current_user.is_admin else current_user.id
    
    projects = project_service.get_recent_projects(user_id=user_id, limit=limit)
    return [ProjectResponse.from_orm(p) for p in projects]


@router.get("/search", response_model=List[ProjectResponse])
async def search_projects(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search projects by name or client name"""
    project_service = ProjectService(db)
    
    # For non-admin users, filter by user
    user_id = None if current_user.is_admin else current_user.id
    
    projects = project_service.search_projects(q, user_id=user_id)
    return [ProjectResponse.from_orm(p) for p in projects]