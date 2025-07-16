import time
from datetime import datetime, timedelta
from typing import Dict, Any

from celery import current_task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.project import Project
from app.services.document import DocumentService
from app.tasks.adjustment_processing import process_adjustments_task


@celery_app.task(bind=True, name="process_document_task")
def process_document_task(self, document_id: int):
    """Process a document and extract data"""
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise Exception(f"Document with ID {document_id} not found")
        
        # Update status to processing
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        # Update task progress
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 20, 'step': 'Starting document processing'}
        )
        
        # Initialize document service
        doc_service = DocumentService(db)
        
        # Step 1: Classify document
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 40, 'step': 'Classifying document'}
        )
        
        doc_service.classify_document(document_id)
        
        # Step 2: Extract data
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 60, 'step': 'Extracting data'}
        )
        
        extracted_data = doc_service.extract_data(document_id)
        
        # Step 3: Update document status
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 80, 'step': 'Finalizing processing'}
        )
        
        document.status = DocumentStatus.COMPLETED
        document.processed_at = datetime.utcnow()
        document.processing_time = int((time.time() - start_time) * 1000)  # milliseconds
        document.processing_notes = "Document processed successfully"
        
        db.commit()
        
        # Update project metrics
        project = db.query(Project).filter(Project.id == document.project_id).first()
        if project:
            project.processed_documents = len([d for d in project.documents if d.is_processed])
            db.commit()
        
        # Step 4: Trigger adjustment processing if appropriate
        if document.document_type in [DocumentType.GENERAL_LEDGER, DocumentType.PROFIT_LOSS, 
                                     DocumentType.BALANCE_SHEET, DocumentType.TRIAL_BALANCE]:
            current_task.update_state(
                state='PROGRESS',
                meta={'progress': 90, 'step': 'Triggering adjustment processing'}
            )
            
            # Queue adjustment processing
            process_adjustments_task.delay(document_id)
        
        # Complete
        current_task.update_state(
            state='SUCCESS',
            meta={'progress': 100, 'step': 'Document processing completed'}
        )
        
        return {
            'document_id': document_id,
            'status': 'completed',
            'processing_time': document.processing_time,
            'extracted_data_preview': str(extracted_data)[:500] if extracted_data else None
        }
        
    except Exception as e:
        # Update document status to error
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.ERROR
            document.error_message = str(e)
            document.processing_time = int((time.time() - start_time) * 1000)
            db.commit()
        
        current_task.update_state(
            state='FAILURE',
            meta={'progress': 0, 'step': 'Error occurred', 'error': str(e)}
        )
        
        raise Exception(f"Document processing failed: {str(e)}")
    
    finally:
        db.close()


@celery_app.task(name="cleanup_expired_documents")
def cleanup_expired_documents():
    """Clean up expired document processing tasks"""
    db = SessionLocal()
    
    try:
        # Find documents that have been processing for more than 30 minutes
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        
        stuck_documents = db.query(Document).filter(
            Document.status == DocumentStatus.PROCESSING,
            Document.updated_at < thirty_minutes_ago
        ).all()
        
        for doc in stuck_documents:
            doc.status = DocumentStatus.ERROR
            doc.error_message = "Processing timeout - document cleanup"
            db.commit()
        
        return f"Cleaned up {len(stuck_documents)} stuck documents"
        
    except Exception as e:
        return f"Error during cleanup: {str(e)}"
    
    finally:
        db.close()


@celery_app.task(name="update_project_metrics")
def update_project_metrics():
    """Update project metrics based on document and adjustment status"""
    db = SessionLocal()
    
    try:
        projects = db.query(Project).all()
        
        for project in projects:
            # Update document metrics
            project.total_documents = len(project.documents)
            project.processed_documents = sum(1 for doc in project.documents if doc.is_processed)
            
            # Update adjustment metrics
            project.total_adjustments = len(project.adjustments)
            project.reviewed_adjustments = sum(1 for adj in project.adjustments if not adj.is_pending)
            
            db.commit()
        
        return f"Updated metrics for {len(projects)} projects"
        
    except Exception as e:
        return f"Error updating metrics: {str(e)}"
    
    finally:
        db.close()


@celery_app.task(name="batch_process_documents")
def batch_process_documents(document_ids: list):
    """Process multiple documents in batch"""
    results = []
    
    for doc_id in document_ids:
        try:
            result = process_document_task.delay(doc_id)
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