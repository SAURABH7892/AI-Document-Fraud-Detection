"""Comprehensive API, Unit, and Integration test suite for DocShield AI."""
import os
import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app
from backend.app.db.session import SessionLocal, Base, engine
from backend.app.db.init_db import init_db
from backend.app.services.file_validation import validate_uploaded_file, FileValidationError
from ai.forensics.analyzer import DocumentForensicsAnalyzer
from ai.field_extraction.academic_extractor import AcademicFieldExtractor
from ai.ocr.engine import OCRPageResult
from ai.risk_engine.engine import RiskEngine
from ai.inference.service import MLInferenceService
from reports.generator import VerificationReportGenerator

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure database tables exist before tests run."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()
    yield

def create_sample_png_bytes(width=200, height=200, color="white"):
    """Helper to create valid PNG image bytes with signature."""
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=color)
    img.save(buf, format="PNG")
    return buf.getvalue()

def create_sample_pdf_bytes():
    """Helper to create minimal valid PDF bytes with %PDF- signature."""
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=300, height=300)
    page.insert_text((50, 50), "UNIVERSITY OF DELHI\nBACHELOR OF TECHNOLOGY\nRoll No: 19CS042\nName: Rahul Sharma\nCGPA: 8.9\nDate: 12-05-2023")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

# ==========================================
# 1. Operational Endpoints Tests
# ==========================================
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ready_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"

# ==========================================
# 2. File Validation Unit Tests
# ==========================================
def test_file_validation_valid_png():
    content = create_sample_png_bytes()
    ext, mime, size, sha = validate_uploaded_file("cert.png", content)
    assert ext == ".png"
    assert mime == "image/png"
    assert size > 0
    assert len(sha) == 64

def test_file_validation_invalid_extension():
    content = b"fake executable"
    with pytest.raises(FileValidationError, match="Unsupported file format"):
        validate_uploaded_file("virus.exe", content)

def test_file_validation_fake_pdf():
    # File named .pdf but containing invalid bytes
    with pytest.raises(FileValidationError, match="File signature verification failed"):
        validate_uploaded_file("fake.pdf", b"this is plain text not pdf")

# ==========================================
# 3. Academic Field Extraction Unit Tests
# ==========================================
def test_academic_field_extraction():
    ocr_result = OCRPageResult(
        page_number=1,
        text="NATIONAL INSTITUTE OF TECHNOLOGY\nCertificate of Degree\nThis is to certify that Aryan Mehra bearing Roll No: 20BCS108 has completed Bachelor of Technology with CGPA: 9.20 on Date of Issue: 15-06-2024.",
        confidence_avg=0.98,
        word_count=28,
        bounding_boxes=[]
    )
    fields = AcademicFieldExtractor.extract_fields([ocr_result])
    assert fields["roll_number"]["value"] == "20BCS108"
    assert fields["student_name"]["value"] == "Aryan Mehra"
    assert "Technology" in fields["degree_course"]["value"]
    assert "9.20" in fields["marks_grade"]["value"]
    assert fields["issue_date"]["value"] == "15-06-2024"

# ==========================================
# 4. Forensics & Risk Engine Unit Tests
# ==========================================
def test_forensics_ela_and_noise():
    import numpy as np
    dummy_img = np.zeros((200, 200, 3), dtype=np.uint8)
    dummy_img[50:150, 50:150] = 255
    findings, features = DocumentForensicsAnalyzer.analyze_page(dummy_img)
    assert len(findings) >= 3
    assert "ela_mean_error" in features
    assert "noise_inconsistency_index" in features

def test_risk_engine_scoring():
    assessment = RiskEngine.evaluate(
        forensic_findings=[],
        ocr_confidence_avg=0.95,
        extracted_fields={
            "student_name": {"value": "John Doe", "confidence": 0.9},
            "institution_name": {"value": "State University", "confidence": 0.9},
            "degree_course": {"value": "B.Tech", "confidence": 0.9}
        },
        issuer_configured=False
    )
    assert assessment.risk_level == "LOW_RISK"
    assert assessment.risk_score < 30.0
    assert "unavailable" in assessment.issuer_verification_status.lower()

# ==========================================
# 5. User Registration & Authentication API Tests
# ==========================================
def test_auth_workflow_and_isolation():
    # Register User A
    user_a_email = "analyst_a@test.com"
    res_a = client.post("/api/v1/auth/register", json={
        "email": user_a_email,
        "password": "SecurePassword123!",
        "full_name": "Analyst A"
    })
    assert res_a.status_code in [201, 400]  # 400 if already created in previous run

    # Login User A
    login_a = client.post("/api/v1/auth/login", json={
        "email": user_a_email,
        "password": "SecurePassword123!"
    })
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Upload document as User A
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = client.post(
        "/api/v1/documents",
        files={"file": ("delhi_univ_cert.pdf", pdf_bytes, "application/pdf")},
        headers=headers_a
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    # Register User B
    user_b_email = "analyst_b@test.com"
    client.post("/api/v1/auth/register", json={
        "email": user_b_email,
        "password": "SecurePassword123!",
        "full_name": "Analyst B"
    })
    login_b = client.post("/api/v1/auth/login", json={
        "email": user_b_email,
        "password": "SecurePassword123!"
    })
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Unauthorized Cross-User Access Test: User B should NOT be able to view User A's document
    cross_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers_b)
    assert cross_res.status_code == 404

    # User A CAN view their own document
    owner_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers_a)
    assert owner_res.status_code == 200
    assert owner_res.json()["original_filename"] == "delhi_univ_cert.pdf"

# ==========================================
# 6. End-to-End Analysis & Report Test
# ==========================================
def test_full_analysis_and_report_generation():
    # Login as demo reviewer
    login_res = client.post("/api/v1/auth/login", json={
        "email": "demo@docshield.ai",
        "password": "DemoPass123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload PDF
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = client.post(
        "/api/v1/documents",
        files={"file": ("btech_degree.pdf", pdf_bytes, "application/pdf")},
        headers=headers
    )
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    import time
    # Wait for the background worker to finish processing
    completed = False
    last_status = None
    for _ in range(60):
        job_res = client.get(f"/api/v1/documents/{doc_id}/job", headers=headers)
        if job_res.status_code == 200:
            last_status = job_res.json()
            if last_status.get("status") == "COMPLETED":
                completed = True
                break
            if last_status.get("status") == "FAILED":
                break
        time.sleep(0.5)
    assert completed, f"Background verification job failed or timed out: {last_status}"

    # Query verification details via API
    detail_res = client.get(f"/api/v1/verifications/by-document/{doc_id}", headers=headers)
    assert detail_res.status_code == 200
    verif_data = detail_res.json()
    assert verif_data["risk_level"] in ["LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"]
    assert len(verif_data["fields"]) > 0
    assert len(verif_data["forensics"]) > 0
    assert "report_id" in verif_data

    # Download verification PDF report
    report_res = client.get(f"/api/v1/verifications/{verif_data['id']}/report", headers=headers)
    assert report_res.status_code == 200
    assert report_res.headers["content-type"] == "application/pdf"
    assert len(report_res.content) > 1000
