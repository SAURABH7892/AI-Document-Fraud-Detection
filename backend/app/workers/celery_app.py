"""Celery distributed task application."""
import logging
from celery import Celery
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "docshield_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per document
)

@celery_app.task(name="tasks.verify_document", bind=True, max_retries=2)
def verify_document_task(self, document_id: str):
    """Celery background task for asynchronous document verification."""
    from backend.app.db.session import SessionLocal
    from backend.app.services.verification_service import VerificationService

    logger.info(f"Celery task started for document_id={document_id}")
    db = SessionLocal()
    try:
        result = VerificationService.execute_verification(document_id, db)
        return result
    except Exception as exc:
        logger.error(f"Celery verification failed: {exc}")
        db.rollback()
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()
