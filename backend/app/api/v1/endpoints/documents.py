"""Document upload, management and retrieval endpoints."""
import os
import io
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.entities import User, Document, VerificationJob, AuditLog
from backend.app.schemas.api_models import DocumentResponse, JobStatusResponse
from backend.app.security.deps import get_current_user
from backend.app.services.file_validation import validate_uploaded_file, FileValidationError
from backend.app.storage import get_storage
from backend.app.workers.dispatcher import dispatch_verification_job

router = APIRouter()

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "academic_certificate",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Securely upload a document (PDF, JPG, PNG), validate mime/magic signature,
    store the original, create the database record, and queue verification job.
    """
    content = await file.read()

    try:
        ext, verified_mime, file_size, sha256_hash = validate_uploaded_file(
            filename=file.filename,
            content=content,
            content_type=file.content_type
        )
    except FileValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    doc_id = str(uuid.uuid4())
    storage_key = f"uploads/{doc_id}/original{ext}"

    # Save to storage
    storage = get_storage()
    storage.save(io.BytesIO(content), storage_key)

    doc = Document(
        id=doc_id,
        user_id=current_user.id,
        original_filename=file.filename,
        storage_key=storage_key,
        mime_type=verified_mime,
        file_size_bytes=file_size,
        file_hash_sha256=sha256_hash,
        document_type=document_type,
        status="QUEUED"
    )
    db.add(doc)

    job = VerificationJob(
        document_id=doc.id,
        status="QUEUED",
        current_stage="QUEUED",
        progress_percent=0
    )
    db.add(job)

    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_UPLOAD",
        resource_type="document",
        resource_id=doc.id,
        details={"filename": file.filename, "size": file_size, "hash": sha256_hash}
    )
    db.add(audit)
    db.commit()
    db.refresh(doc)

    # Dispatch asynchronous analysis job
    dispatch_verification_job(doc.id)

    return DocumentResponse.model_validate(doc)

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents owned by the authenticated user."""
    query = db.query(Document).filter(Document.user_id == current_user.id)
    if search:
        query = query.filter(Document.original_filename.ilike(f"%{search}%"))
    
    docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return [DocumentResponse.model_validate(d) for d in docs]

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve document details with ownership enforcement."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentResponse.model_validate(doc)

@router.get("/{document_id}/job", response_model=JobStatusResponse)
def get_document_job_status(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time job execution status and progress percentage."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    job = db.query(VerificationJob).filter(VerificationJob.document_id == document_id).order_by(VerificationJob.created_at.desc()).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification job not found.")
    
    return JobStatusResponse.model_validate(job)

@router.get("/{document_id}/file")
def get_original_file(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download original document content (authorized owner only)."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    
    storage = get_storage()
    try:
        file_bytes = storage.get(doc.storage_key)
        return Response(
            content=file_bytes,
            media_type=doc.mime_type,
            headers={"Content-Disposition": f'inline; filename="{doc.original_filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File content unavailable.")

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete document, physical storage files, and all associated verification records."""
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    storage = get_storage()
    try:
        storage.delete(doc.storage_key)
    except Exception:
        pass

    db.delete(doc)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_DELETED",
        resource_type="document",
        resource_id=document_id
    )
    db.add(audit)
    db.commit()

    return {"message": "Document and associated findings deleted successfully."}
