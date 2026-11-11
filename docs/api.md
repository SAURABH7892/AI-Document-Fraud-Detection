# DocShield AI — REST API Documentation

Base URL: `http://localhost:8000/api/v1`  
Interactive OpenAPI Documentation: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Creates a new analyst/reviewer account.
- **Request Body:**
```json
{
  "email": "analyst@university.edu",
  "password": "SecurePassword123!",
  "full_name": "Dr. Raman Kumar",
  "role": "analyst"
}
```
- **Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "c1f74f76-8f24-4f0e-b7a4-325bdf9bce01",
    "email": "analyst@university.edu",
    "full_name": "Dr. Raman Kumar",
    "role": "analyst",
    "is_active": true,
    "created_at": "2026-10-10T11:00:00Z"
  }
}
```

### `POST /auth/login`
Authenticates user and returns JWT Bearer access token.
- **Request Body:**
```json
{
  "email": "demo@docshield.ai",
  "password": "DemoPass123!"
}
```

### `GET /auth/me`
Retrieves authenticated user profile.
- **Header:** `Authorization: Bearer <token>`

---

## 2. Document Management Endpoints

### `POST /documents`
Uploads a document for analysis. Server enforces MIME validation, file magic byte checks, and SHA-256 calculation.
- **Content-Type:** `multipart/form-data`
- **Fields:**
  - `file`: Binary file (PDF, JPG, PNG, max 15MB)
  - `document_type`: "academic_certificate"
- **Response (201 Created):**
```json
{
  "id": "eed51d6f-9662-4346-a1d8-8e033461cccb",
  "original_filename": "btech_degree.pdf",
  "mime_type": "application/pdf",
  "file_size_bytes": 104250,
  "file_hash_sha256": "3a7b...48fe",
  "document_type": "academic_certificate",
  "status": "QUEUED",
  "page_count": 1,
  "created_at": "2026-10-10T11:05:00Z",
  "updated_at": "2026-10-10T11:05:00Z"
}
```

### `GET /documents`
Lists documents owned by the authenticated user with optional `?search=` and pagination.

### `GET /documents/{document_id}`
Retrieves document metadata. Enforces ownership authorization.

### `GET /documents/{document_id}/job`
Retrieves background worker processing status and stage progress percent (0-100%).

### `GET /documents/{document_id}/file`
Downloads/views original uploaded file.

### `DELETE /documents/{document_id}`
Permanently deletes document, extracted findings, and storage files.

---

## 3. Verification & Forensics Endpoints

### `GET /verifications/by-document/{document_id}`
Retrieves complete forensic integrity results, extracted academic fields, and ML predictions.

### `GET /verifications/{verification_id}/report`
Downloads the official ReportLab generated multi-page PDF verification report.
- **Response:** `Content-Type: application/pdf` with `Content-Disposition: attachment; filename="DocShield_Report_...pdf"`

### `GET /verifications/documents/{document_id}/artifacts/ela`
Streams the generated Error Level Analysis difference heatmap image.

---

## 4. Operational & Health Endpoints

### `GET /health`
Liveness probe returning service status.

### `GET /ready`
Readiness probe testing database connection, storage readiness, and worker mode.
