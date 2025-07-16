from celery import Celery
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.document import DocumentService
from app.ai.adjustment_workflow import AdjustmentWorkflow
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "qoe_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.document_tasks.*": {"queue": "document_processing"},
        "app.tasks.adjustment_tasks.*": {"queue": "adjustment_processing"},
    }
)

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    """Process a document and extract metadata"""
    db = SessionLocal()
    try:
        logger.info(f"Processing document {document_id}")
        
        # Get document service
        document_service = DocumentService(db)
        
        # Process the document
        document = document_service.process_document(document_id)
        
        logger.info(f"Document {document_id} processed successfully")
        
        # If document is processed successfully, trigger adjustment workflow
        if document.status == "completed":
            trigger_adjustment_workflow.delay(document_id)
        
        return {
            "status": "success",
            "document_id": document_id,
            "message": "Document processed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update document status to error
        try:
            document_service = DocumentService(db)
            document = document_service.get_by_id(document_id)
            if document:
                document.status = "error"
                document.error_message = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"Error updating document status: {str(db_error)}")
        
        # Retry task
        try:
            raise self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for document {document_id}")
            return {
                "status": "error",
                "document_id": document_id,
                "message": str(e)
            }
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def trigger_adjustment_workflow(self, document_id: int):
    """Trigger AI adjustment workflow for a processed document"""
    db = SessionLocal()
    try:
        logger.info(f"Triggering adjustment workflow for document {document_id}")
        
        # Get document
        document_service = DocumentService(db)
        document = document_service.get_by_id(document_id)
        
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Initialize adjustment workflow
        workflow = AdjustmentWorkflow()
        
        # Run the workflow
        result = workflow.run(document_id)
        
        logger.info(f"Adjustment workflow completed for document {document_id}")
        
        return {
            "status": "success",
            "document_id": document_id,
            "adjustments_created": result.get("adjustments_created", 0),
            "message": "Adjustment workflow completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in adjustment workflow for document {document_id}: {str(e)}")
        
        # Retry task
        try:
            raise self.retry(countdown=60, exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for adjustment workflow {document_id}")
            return {
                "status": "error",
                "document_id": document_id,
                "message": str(e)
            }
    finally:
        db.close()

@celery_app.task
def cleanup_temp_files():
    """Clean up temporary files and old uploads"""
    import os
    import time
    
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            return {"status": "success", "message": "No upload directory found"}
        
        # Clean up files older than 7 days
        cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days ago
        cleaned_files = 0
        
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                cleaned_files += 1
        
        logger.info(f"Cleaned up {cleaned_files} temporary files")
        
        return {
            "status": "success",
            "cleaned_files": cleaned_files,
            "message": f"Cleaned up {cleaned_files} temporary files"
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-temp-files": {
        "task": "app.tasks.document_tasks.cleanup_temp_files",
        "schedule": 60.0 * 60.0 * 24.0,  # Run daily
    },
}
celery_app.conf.timezone = "UTC"