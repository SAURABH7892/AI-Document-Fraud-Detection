"""Pydantic schemas for API request and response serialization."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# User Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    role: Optional[str] = "analyst"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Document Schemas
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    file_hash_sha256: str
    document_type: str
    status: str
    page_count: int
    created_at: datetime
    updated_at: datetime

# Verification Result Schemas
class DocumentFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    field_name: str
    field_value: Optional[str]
    confidence: float
    bounding_box: Optional[Any] = None

class ForensicFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feature_name: str
    measured_value: float
    threshold: float
    severity: str
    explanation: str
    localized_regions: List[Any] = []

class ModelPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model_name: str
    model_version: str
    fraud_probability: Optional[float] = None
    prediction_label: str
    feature_vector: Optional[Dict[str, Any]] = None

class VerificationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    risk_level: str
    risk_score: float
    summary_evidence: List[Dict[str, Any]]
    issuer_verification_status: str
    recommendation: str
    created_at: datetime
    document: DocumentResponse
    fields: List[DocumentFieldResponse]
    forensics: List[ForensicFindingResponse]
    ml_prediction: Optional[ModelPredictionResponse] = None
    report_id: Optional[str] = None

# Job Status Schema
class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    status: str
    current_stage: str
    progress_percent: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Dashboard Statistics Schema
class DashboardStatsResponse(BaseModel):
    total_documents: int
    completed_verifications: int
    pending_jobs: int
    failed_jobs: int
    risk_distribution: Dict[str, int]
    recent_documents: List[DocumentResponse]
