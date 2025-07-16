from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.adjustment import Adjustment as AdjustmentModel
from app.schemas.adjustment import AdjustmentCreate, AdjustmentUpdate, AdjustmentResponse, AdjustmentReview
from app.services.adjustment import AdjustmentService

router = APIRouter()

@router.get("/", response_model=List[AdjustmentResponse])
def get_adjustments(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all adjustments with optional filtering"""
    adjustments = AdjustmentService.get_adjustments(
        db, project_id=project_id, status=status, skip=skip, limit=limit
    )
    return adjustments

@router.get("/{adjustment_id}", response_model=AdjustmentResponse)
def get_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific adjustment by ID"""
    adjustment = AdjustmentService.get_adjustment(db, adjustment_id)
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    return adjustment

@router.post("/", response_model=AdjustmentResponse)
def create_adjustment(
    adjustment_data: AdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new adjustment"""
    adjustment = AdjustmentService.create_adjustment(db, adjustment_data, current_user.id)
    return adjustment

@router.put("/{adjustment_id}", response_model=AdjustmentResponse)
def update_adjustment(
    adjustment_id: int,
    adjustment_update: AdjustmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an adjustment"""
    adjustment = AdjustmentService.update_adjustment(db, adjustment_id, adjustment_update)
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    return adjustment

@router.post("/{adjustment_id}/review")
def review_adjustment(
    adjustment_id: int,
    review_data: AdjustmentReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Review an adjustment"""
    adjustment = AdjustmentService.review_adjustment(
        db, adjustment_id, review_data, current_user.id
    )
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    return {"message": "Adjustment reviewed successfully", "adjustment": adjustment}

@router.delete("/{adjustment_id}")
def delete_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an adjustment"""
    success = AdjustmentService.delete_adjustment(db, adjustment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Adjustment not found")
    return {"message": "Adjustment deleted successfully"}