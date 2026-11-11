"""Verification results, analysis dispatch, and report download endpoints."""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.entities import (
    User, Document, VerificationJob, VerificationResult,
    DocumentField, ForensicResult, ModelPrediction, Report, AuditLog
)
from backend.app.schemas.api_models import (
    VerificationDetailResponse, DocumentResponse, DocumentFieldResponse,
    ForensicFindingResponse, ModelPredictionResponse
)
from backend.app.security.deps import get_current_user
from backend.app.core.config import settings
from backend.app.workers.dispatcher import dispatch_verification_job

router = APIRouter()

@router.post("/documents/{document_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
def trigger_analysis(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger or re-run analysis job for a document."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    doc.status = "QUEUED"
    job = VerificationJob(
        document_id=doc.id,
        status="QUEUED",
        current_stage="QUEUED",
        progress_percent=0
    )
    db.add(job)
    db.commit()

    dispatch_verification_job(doc.id)
    return {"message": "Verification analysis job queued.", "document_id": doc.id}

@router.get("/by-document/{document_id}", response_model=VerificationDetailResponse)
def get_verification_by_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve complete verification results for a given document."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    verif = db.query(VerificationResult).filter(VerificationResult.document_id == document_id).order_by(VerificationResult.created_at.desc()).first()
    if not verif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification analysis not yet completed for this document.")

    fields = db.query(DocumentField).filter(DocumentField.document_id == document_id).all()
    forensics = db.query(ForensicResult).filter(ForensicResult.document_id == document_id).all()
    ml_pred = db.query(ModelPrediction).filter(ModelPrediction.document_id == document_id).order_by(ModelPrediction.created_at.desc()).first()
    report = db.query(Report).filter(Report.document_id == document_id).order_by(Report.created_at.desc()).first()

    return VerificationDetailResponse(
        id=verif.id,
        document_id=doc.id,
        risk_level=verif.risk_level,
        risk_score=verif.risk_score,
        summary_evidence=verif.summary_evidence or [],
        issuer_verification_status=verif.issuer_verification_status,
        recommendation=verif.recommendation,
        created_at=verif.created_at,
        document=DocumentResponse.model_validate(doc),
        fields=[DocumentFieldResponse.model_validate(f) for f in fields],
        forensics=[ForensicFindingResponse.model_validate(f) for f in forensics],
        ml_prediction=ModelPredictionResponse.model_validate(ml_pred) if ml_pred else None,
        report_id=report.id if report else None,
        issuer_metadata=getattr(verif, 'issuer_metadata', None)
    )

@router.get("/{verification_id}", response_model=VerificationDetailResponse)
def get_verification(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve verification results by verification ID."""
    verif = db.query(VerificationResult).filter(VerificationResult.id == verification_id).first()
    if not verif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found.")

    doc = db.query(Document).filter(Document.id == verif.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document.")

    return get_verification_by_document(doc.id, db, current_user)

@router.get("/{verification_id}/report")
def download_verification_report(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the official verification PDF report."""
    verif = db.query(VerificationResult).filter(VerificationResult.id == verification_id).first()
    if not verif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found.")

    doc = db.query(Document).filter(Document.id == verif.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    report = db.query(Report).filter(Report.verification_result_id == verification_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report PDF not found.")

    report_abs_path = os.path.join(settings.STORAGE_LOCAL_PATH, report.report_storage_key)
    if not os.path.exists(report_abs_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found on storage.")

    report.download_count += 1
    
    audit = AuditLog(
        user_id=current_user.id,
        action="REPORT_DOWNLOAD",
        resource_type="report",
        resource_id=report.id
    )
    db.add(audit)
    db.commit()

    return FileResponse(
        path=report_abs_path,
        media_type="application/pdf",
        filename=f"DocShield_Report_{doc.original_filename}.pdf"
    )

@router.get("/documents/{document_id}/report")
def download_report_by_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the official verification PDF report directly using document_id."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    report = db.query(Report).filter(Report.document_id == document_id).order_by(Report.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report PDF not found for this document.")

    report_abs_path = os.path.join(settings.STORAGE_LOCAL_PATH, report.report_storage_key)
    if not os.path.exists(report_abs_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found on storage.")

    report.download_count += 1
    db.commit()

    return FileResponse(
        path=report_abs_path,
        media_type="application/pdf",
        filename=f"DocShield_Report_{doc.original_filename}.pdf"
    )

@router.get("/documents/{document_id}/artifacts/ela")
def get_ela_artifact(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serve the generated Error Level Analysis heatmap image for frontend display."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    ela_path = os.path.join(settings.STORAGE_LOCAL_PATH, "artifacts", document_id, "ela_analysis.jpg")
    if not os.path.exists(ela_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ELA visual artifact not available.")

    return FileResponse(
        path=ela_path,
        media_type="image/jpeg",
        filename=f"ela_{document_id}.jpg"
    )
