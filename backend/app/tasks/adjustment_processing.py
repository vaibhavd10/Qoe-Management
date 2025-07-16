import time
from datetime import datetime
from typing import Dict, Any, List

from celery import current_task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.project import Project
from app.models.adjustment import Adjustment, AdjustmentStatus
from app.ai.adjustment_workflow import adjustment_workflow
from app.services.project import ProjectService


@celery_app.task(bind=True, name="process_adjustments_task")
def process_adjustments_task(self, document_id: int):
    """Process adjustments for a document using AI workflow"""
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise Exception(f"Document with ID {document_id} not found")
        
        # Get project
        project = db.query(Project).filter(Project.id == document.project_id).first()
        if not project:
            raise Exception(f"Project not found for document {document_id}")
        
        # Update task progress
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'step': 'Starting adjustment processing'}
        )
        
        # Check if document has extracted data
        if not document.extracted_data:
            raise Exception("Document has no extracted data")
        
        # Step 1: Run AI workflow
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'step': 'Running AI adjustment workflow'}
        )
        
        ai_adjustments = adjustment_workflow.run_workflow(
            document_data=document.extracted_data,
            document_type=document.document_type,
            materiality_threshold=project.materiality_threshold,
            materiality_percentage=project.materiality_percentage
        )
        
        # Step 2: Create adjustment records
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 60, 'step': 'Creating adjustment records'}
        )
        
        created_adjustments = []
        for ai_adj in ai_adjustments:
            try:
                adjustment = Adjustment(
                    title=ai_adj.get('title', 'Unknown Adjustment'),
                    description=ai_adj.get('description', ''),
                    adjustment_type=ai_adj.get('adjustment_type'),
                    amount=ai_adj.get('amount', 0),
                    debit_account=ai_adj.get('debit_account'),
                    credit_account=ai_adj.get('credit_account'),
                    account_impact=ai_adj.get('account_impact'),
                    narrative=ai_adj.get('narrative'),
                    confidence_score=ai_adj.get('confidence_score', 0.0),
                    rule_applied=ai_adj.get('rule_applied'),
                    is_material=ai_adj.get('is_material', False),
                    materiality_reason=ai_adj.get('materiality_reason'),
                    project_id=document.project_id,
                    source_document_id=document.id,
                    created_by=document.uploaded_by,
                    processing_time=int((time.time() - start_time) * 1000),
                    ai_model_used="gpt-4-turbo-preview"
                )
                
                db.add(adjustment)
                created_adjustments.append(adjustment)
                
            except Exception as e:
                # Log error but continue with other adjustments
                print(f"Error creating adjustment: {str(e)}")
                continue
        
        db.commit()
        
        # Step 3: Update project metrics
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 80, 'step': 'Updating project metrics'}
        )
        
        project_service = ProjectService(db)
        project_service.update_metrics(project.id)
        
        # Step 4: Complete processing
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 100, 'step': 'Adjustment processing completed'}
        )
        
        return {
            'document_id': document_id,
            'project_id': project.id,
            'adjustments_created': len(created_adjustments),
            'processing_time': int((time.time() - start_time) * 1000),
            'ai_adjustments': len(ai_adjustments)
        }
        
    except Exception as e:
        current_task.update_state(
            state='FAILURE',
            meta={'progress': 0, 'step': 'Error occurred', 'error': str(e)}
        )
        
        raise Exception(f"Adjustment processing failed: {str(e)}")
    
    finally:
        db.close()


@celery_app.task(name="batch_process_adjustments")
def batch_process_adjustments(document_ids: List[int]):
    """Process adjustments for multiple documents"""
    results = []
    
    for doc_id in document_ids:
        try:
            result = process_adjustments_task.delay(doc_id)
            results.append({
                'document_id': doc_id,
                'task_id': result.id,
                'status': 'queued'
            })
        except Exception as e:
            results.append({
                'document_id': doc_id,
                'status': 'error',
                'error': str(e)
            })
    
    return results


@celery_app.task(name="reprocess_adjustment")
def reprocess_adjustment(adjustment_id: int):
    """Reprocess a single adjustment with updated AI analysis"""
    db = SessionLocal()
    
    try:
        adjustment = db.query(Adjustment).filter(Adjustment.id == adjustment_id).first()
        if not adjustment:
            raise Exception(f"Adjustment with ID {adjustment_id} not found")
        
        # Get source document
        if adjustment.source_document_id:
            document = db.query(Document).filter(Document.id == adjustment.source_document_id).first()
            if document and document.extracted_data:
                # Get project
                project = db.query(Project).filter(Project.id == adjustment.project_id).first()
                
                # Run AI workflow for single adjustment
                ai_adjustments = adjustment_workflow.run_workflow(
                    document_data=document.extracted_data,
                    document_type=document.document_type,
                    materiality_threshold=project.materiality_threshold,
                    materiality_percentage=project.materiality_percentage
                )
                
                # Find matching adjustment and update
                for ai_adj in ai_adjustments:
                    if ai_adj.get('adjustment_type') == adjustment.adjustment_type:
                        # Update existing adjustment
                        adjustment.narrative = ai_adj.get('narrative', adjustment.narrative)
                        adjustment.confidence_score = ai_adj.get('confidence_score', adjustment.confidence_score)
                        adjustment.is_material = ai_adj.get('is_material', adjustment.is_material)
                        adjustment.materiality_reason = ai_adj.get('materiality_reason', adjustment.materiality_reason)
                        adjustment.updated_at = datetime.utcnow()
                        break
                
                db.commit()
        
        return {
            'adjustment_id': adjustment_id,
            'status': 'reprocessed',
            'updated_at': adjustment.updated_at.isoformat()
        }
        
    except Exception as e:
        return {
            'adjustment_id': adjustment_id,
            'status': 'error',
            'error': str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="calculate_project_adjustments_summary")
def calculate_project_adjustments_summary(project_id: int):
    """Calculate summary metrics for project adjustments"""
    db = SessionLocal()
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project with ID {project_id} not found")
        
        adjustments = project.adjustments
        
        # Calculate summary metrics
        total_adjustments = len(adjustments)
        accepted_adjustments = sum(1 for adj in adjustments if adj.is_accepted)
        rejected_adjustments = sum(1 for adj in adjustments if adj.is_rejected)
        pending_adjustments = sum(1 for adj in adjustments if adj.is_pending)
        material_adjustments = sum(1 for adj in adjustments if adj.is_material)
        
        total_amount = sum(adj.amount for adj in adjustments if adj.is_accepted)
        avg_confidence = sum(adj.confidence_score for adj in adjustments) / total_adjustments if total_adjustments > 0 else 0
        
        # Group by adjustment type
        by_type = {}
        for adj in adjustments:
            adj_type = adj.adjustment_type.value
            if adj_type not in by_type:
                by_type[adj_type] = {'count': 0, 'amount': 0}
            by_type[adj_type]['count'] += 1
            by_type[adj_type]['amount'] += adj.amount
        
        summary = {
            'project_id': project_id,
            'total_adjustments': total_adjustments,
            'accepted_adjustments': accepted_adjustments,
            'rejected_adjustments': rejected_adjustments,
            'pending_adjustments': pending_adjustments,
            'material_adjustments': material_adjustments,
            'total_amount': total_amount,
            'avg_confidence': avg_confidence,
            'by_type': by_type,
            'calculated_at': datetime.utcnow().isoformat()
        }
        
        return summary
        
    except Exception as e:
        return {
            'project_id': project_id,
            'status': 'error',
            'error': str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="auto_approve_high_confidence_adjustments")
def auto_approve_high_confidence_adjustments(project_id: int, confidence_threshold: float = 0.9):
    """Auto-approve adjustments with high confidence scores"""
    db = SessionLocal()
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project with ID {project_id} not found")
        
        # Find high confidence pending adjustments
        high_confidence_adjustments = db.query(Adjustment).filter(
            Adjustment.project_id == project_id,
            Adjustment.status == AdjustmentStatus.PENDING,
            Adjustment.confidence_score >= confidence_threshold
        ).all()
        
        approved_count = 0
        for adjustment in high_confidence_adjustments:
            adjustment.status = AdjustmentStatus.ACCEPTED
            adjustment.reviewed_at = datetime.utcnow()
            adjustment.reviewer_notes = f"Auto-approved (confidence: {adjustment.confidence_score:.2f})"
            approved_count += 1
        
        db.commit()
        
        # Update project metrics
        project_service = ProjectService(db)
        project_service.update_metrics(project_id)
        
        return {
            'project_id': project_id,
            'approved_count': approved_count,
            'confidence_threshold': confidence_threshold
        }
        
    except Exception as e:
        return {
            'project_id': project_id,
            'status': 'error',
            'error': str(e)
        }
    
    finally:
        db.close()