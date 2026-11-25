"""Task dispatcher supporting Celery and concurrent local thread pool."""
import logging
from concurrent.futures import ThreadPoolExecutor
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Local in-process thread pool for zero-dependency execution
_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="docshield_worker")

def _run_in_background(document_id: str):
    """Execute verification in threadpool."""
    from backend.app.db.session import SessionLocal
    from backend.app.services.verification_service import VerificationService
    
    db = SessionLocal()
    try:
        VerificationService.execute_verification(document_id, db)
    except Exception as e:
        logger.error(f"Background thread verification error for {document_id}: {e}")
    finally:
        db.close()

def dispatch_verification_job(document_id: str):
    """Dispatch document verification job based on WORKER_MODE."""
    if settings.WORKER_MODE.lower() == "celery":
        try:
            from backend.app.workers.celery_app import verify_document_task
            verify_document_task.delay(document_id)
            logger.info(f"Dispatched document {document_id} to Celery queue.")
            return "celery"
        except Exception as e:
            logger.warning(f"Failed to enqueue to Celery ({e}). Falling back to in-process thread worker.")
            _executor.submit(_run_in_background, document_id)
            return "inline_fallback"
    else:
        _executor.submit(_run_in_background, document_id)
        logger.info(f"Dispatched document {document_id} to in-process worker thread.")
        return "inline"
