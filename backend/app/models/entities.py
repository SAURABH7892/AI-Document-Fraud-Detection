"""SQLAlchemy database models for DocShield AI."""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst", nullable=False)  # admin, analyst, reviewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False, index=True)
    document_type = Column(String(100), default="academic_certificate", nullable=False)
    status = Column(String(50), default="UPLOADED", nullable=False, index=True)  # UPLOADED, QUEUED, PROCESSING, COMPLETED, FAILED
    page_count = Column(Integer, default=1)
    metadata_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="documents")
    jobs = relationship("VerificationJob", back_populates="document", cascade="all, delete-orphan")
    ocr_results = relationship("OCRResult", back_populates="document", cascade="all, delete-orphan")
    fields = relationship("DocumentField", back_populates="document", cascade="all, delete-orphan")
    forensic_results = relationship("ForensicResult", back_populates="document", cascade="all, delete-orphan")
    model_predictions = relationship("ModelPrediction", back_populates="document", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="document", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="document", cascade="all, delete-orphan")


class VerificationJob(Base):
    __tablename__ = "verification_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="QUEUED", nullable=False)  # QUEUED, PROCESSING, COMPLETED, FAILED
    current_stage = Column(String(100), default="INITIALIZING")
    progress_percent = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="jobs")


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, default=1, nullable=False)
    extracted_text = Column(Text, default="", nullable=False)
    confidence_avg = Column(Float, default=0.0, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    bounding_boxes = Column(JSON, default=list)  # list of {text, confidence, bbox: [x, y, w, h]}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="ocr_results")


class DocumentField(Base):
    __tablename__ = "document_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)  # student_name, institution_name, degree_course, roll_number, etc.
    field_value = Column(String(512), nullable=True)
    confidence = Column(Float, default=0.0, nullable=False)
    bounding_box = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="fields")


class ForensicResult(Base):
    __tablename__ = "forensic_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(100), nullable=False)  # ela_variance, noise_inconsistency, layout_alignment, etc.
    measured_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH
    explanation = Column(Text, nullable=False)
    localized_regions = Column(JSON, default=list)  # coordinates of anomalies
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="forensic_results")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    fraud_probability = Column(Float, nullable=False)
    prediction_label = Column(String(50), nullable=False)  # AUTHENTIC, TAMPERED, SUSPICIOUS
    feature_vector = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="model_predictions")


class VerificationSource(Base):
    __tablename__ = "verification_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_name = Column(String(100), unique=True, nullable=False)  # DigiLocker / NAD, Barcode API, etc.
    is_available = Column(Boolean, default=False, nullable=False)
    status_details = Column(String(255), default="Not configured")
    last_checked_at = Column(DateTime, default=datetime.utcnow)


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_level = Column(String(50), default="INCONCLUSIVE", nullable=False)  # LOW_RISK, MEDIUM_RISK, HIGH_RISK, INCONCLUSIVE
    risk_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0
    summary_evidence = Column(JSON, default=list)
    issuer_verification_status = Column(String(512), default="Issuer verification unavailable (Not configured)", nullable=False)
    issuer_metadata = Column(JSON, default=dict)
    recommendation = Column(Text, default="Human review recommended.")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="verification_results")
    reports = relationship("Report", back_populates="verification_result", cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    verification_result_id = Column(String(36), ForeignKey("verification_results.id", ondelete="CASCADE"), nullable=False, index=True)
    report_storage_key = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="reports")
    verification_result = relationship("VerificationResult", back_populates="reports")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # USER_REGISTER, USER_LOGIN, DOCUMENT_UPLOAD, DOCUMENT_ANALYSIS, REPORT_DOWNLOAD
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")
