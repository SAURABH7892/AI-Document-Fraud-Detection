"""Dashboard analytics and statistics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.models.entities import User, Document, VerificationJob, VerificationResult
from backend.app.schemas.api_models import DashboardStatsResponse, DocumentResponse
from backend.app.security.deps import get_current_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aggregate genuine real-time statistics for the authenticated user's dashboard."""
    # Total documents
    total_docs = db.query(Document).filter(Document.user_id == current_user.id).count()

    # Completed verifications
    completed = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.status == "COMPLETED"
    ).count()

    # Pending jobs (QUEUED or PROCESSING)
    pending = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.status.in_(["QUEUED", "PROCESSING"])
    ).count()

    # Failed jobs
    failed = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.status == "FAILED"
    ).count()

    # Risk level distribution from completed verifications
    results = (
        db.query(VerificationResult.risk_level, func.count(VerificationResult.id))
        .join(Document, VerificationResult.document_id == Document.id)
        .filter(Document.user_id == current_user.id)
        .group_by(VerificationResult.risk_level)
        .all()
    )

    risk_dist = {
        "LOW_RISK": 0,
        "MEDIUM_RISK": 0,
        "HIGH_RISK": 0,
        "INCONCLUSIVE": 0
    }
    for level, count in results:
        if level in risk_dist:
            risk_dist[level] = count

    # Recent 6 documents
    recent_docs = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .limit(6)
        .all()
    )

    return DashboardStatsResponse(
        total_documents=total_docs,
        completed_verifications=completed,
        pending_jobs=pending,
        failed_jobs=failed,
        risk_distribution=risk_dist,
        recent_documents=[DocumentResponse.model_validate(d) for d in recent_docs]
    )
