from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "qoe_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.document_processing",
        "app.tasks.adjustment_processing",
        "app.tasks.report_generation",
        "app.tasks.questionnaire_tasks",
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routes
celery_app.conf.task_routes = {
    "app.tasks.document_processing.*": {"queue": "document_processing"},
    "app.tasks.adjustment_processing.*": {"queue": "adjustment_processing"},
    "app.tasks.report_generation.*": {"queue": "report_generation"},
    "app.tasks.questionnaire_tasks.*": {"queue": "questionnaire"},
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-tasks": {
        "task": "app.tasks.cleanup_expired_tasks",
        "schedule": 3600.0,  # Run every hour
    },
    "update-project-metrics": {
        "task": "app.tasks.update_project_metrics",
        "schedule": 300.0,  # Run every 5 minutes
    },
}

if __name__ == "__main__":
    celery_app.start()