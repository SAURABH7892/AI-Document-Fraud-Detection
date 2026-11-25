# DocShield AI — Implementation Plan & Milestone Roadmap

## Project Metadata
- **Project Name:** DocShield AI — AI-Based Document Fraud Detection and Verification System
- **Academic Context:** B.Tech Major Project (Academic Session 2026–27)
- **Team:** Vaibhav (AI/ML & Backend Lead) & Saurabh (Full-Stack & Deployment Lead)
- **Primary Domain:** Academic Certificates & Mark Sheets (extensible architecture)

---

## Architecture Principles & Ground Rules
1. **Truthfulness Guarantee:** Never fabricate processing results, model metrics, issuer responses, or deployment statuses. Genuine outputs only.
2. **Explainability First:** Provide multi-signal forensic evidence (Error Level Analysis, layout consistency, noise variance, metadata anomalies) rather than opaque black-box labels.
3. **Decoupled Architecture:** Clean separation between frontend (Next.js), REST API (FastAPI), AI/CV/OCR services, background task workers, and persistent storage.
4. **Resilient Local Execution:** Zero-config local development support (local file storage adapter, async background worker fallback, SQLite/PostgreSQL switchable backend) while fully containerized for production (Docker, PostgreSQL, Redis, Celery).

---

## Phase Checklist & Deliverables

- [ ] **Phase 1: Inspection, Planning & Architecture**
  - [x] Workspace inspection and toolchain verification (Python 3.11, Node 22, npm, pip, git).
  - [x] `docs/implementation_plan.md` created.
  - [x] `docs/architecture.md` created.
  - [x] Directory structure planned.

- [ ] **Phase 2: Project Skeleton & Tooling Setup**
  - [ ] Root configuration: `.gitignore`, `.env.example`, `docker-compose.yml`, `README.md`.
  - [ ] Backend structure (`backend/app`, `pyproject.toml`, `requirements.txt`).
  - [ ] AI module structure (`ai/ocr`, `ai/forensics`, `ai/features`, `ai/training`, `ai/inference`).
  - [ ] Frontend setup (`frontend/` Next.js App Router, Tailwind CSS, TypeScript).
  - [ ] Backend health and readiness endpoints (`/health`, `/ready`).

- [ ] **Phase 3: Database & Authentication Engine**
  - [ ] SQLAlchemy database schema and models:
    - `users`, `documents`, `verification_jobs`, `ocr_results`, `document_fields`, `forensic_results`, `model_predictions`, `verification_sources`, `verification_results`, `reports`, `audit_logs`.
  - [ ] Secure password hashing (bcrypt / argon2) and JWT token creation/verification.
  - [ ] Auth endpoints: `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`.
  - [ ] User ownership checks & access control middleware.

- [ ] **Phase 4: Secure Document Upload & Storage Adapter**
  - [ ] Pluggable Storage Service: `LocalStorageAdapter` and `S3StorageAdapter` interface.
  - [ ] Secure server-side validation: MIME type, file signature (magic bytes), file extension (.pdf, .jpg, .jpeg, .png), size limit (15MB).
  - [ ] UUIDv4 document tracking and isolated storage paths.
  - [ ] Document endpoints: `POST /api/v1/documents`, `GET /api/v1/documents`, `GET /api/v1/documents/{id}`, `DELETE /api/v1/documents/{id}`.

- [ ] **Phase 5: Document Preprocessing, OCR & Academic Field Extraction**
  - [ ] PyMuPDF renderer for multi-page PDF to high-resolution image conversion.
  - [ ] Image preprocessing (grayscale, adaptive thresholding, deskewing, noise reduction).
  - [ ] Modular OCR service (EasyOCR engine with bounding boxes, character/word confidence, line clustering).
  - [ ] Academic field extraction rules:
    - Student Name, Institution Name, Course / Degree, Roll / Registration Number, Certificate ID, Issue Date, Marks / CGPA / Grade.
  - [ ] Field confidence calculation and uncertainty tracking.

- [ ] **Phase 6: Computer Vision & Digital Forensics Pipeline**
  - [ ] Error Level Analysis (ELA) service: Resaving at standard JPEG quality, pixel difference matrix, suspicious high-error region localization.
  - [ ] Noise & Texture Consistency: Local Laplacian variance, standard deviation across grid blocks to detect spliced patches.
  - [ ] Layout & Typography Alignment: Text line slope analysis, baseline anomalies, anomalous font size variance.
  - [ ] Edge & Compression Discontinuity: Gradient magnitude analysis, JPEG grid artifact detection.
  - [ ] PDF Metadata Forensics: Inspection of producer/creator, modification timestamps, incremental update anomalies, software tags (e.g. Photoshop / Canva).
  - [ ] Suspicious Region Locator: Generating bounding boxes and heatmap masks for frontend visualization.

- [ ] **Phase 7: ML Training, Evaluation & Inference Pipeline**
  - [ ] Documented feature schema: 18-dimensional feature vector combining OCR stats, forensic signals, layout variance, and metadata indicators.
  - [ ] Dataset generator script: Generates labeled authentic and controlled tampered academic documents with grouped splits (70/15/15) to prevent data leakage.
  - [ ] Supervised model training: Random Forest and XGBoost baseline classifiers.
  - [ ] Evaluation suite: Accuracy, Precision, Recall, F1-Score, Confusion Matrix, ROC-AUC.
  - [ ] Model artifact serialization and inference service.
  - [ ] Honest status: Explicit "Model not trained / unavailable" when weights are absent.

- [ ] **Phase 8: Explainable Risk Engine & PDF Report Generator**
  - [ ] Multi-signal Risk Engine: Combining forensic anomaly metrics, OCR consistency, metadata alerts, and ML predictions.
  - [ ] Calibrated risk scoring (0-100 score, Low / Medium / High / Inconclusive risk categories).
  - [ ] Issuer verification connector interface (reporting DigiLocker/NAD status as "Not configured / Unavailable" truthfully).
  - [ ] ReportLab PDF generator: Multi-page document integrity certificate with audit trail, forensic charts, extracted fields, and review recommendations.
  - [ ] Verification endpoints: `POST /api/v1/documents/{id}/analyze`, `GET /api/v1/verifications/{id}`, `GET /api/v1/verifications/{id}/report`.

- [ ] **Phase 9: Next.js Frontend Application**
  - [ ] Landing page (`/`): Academic document fraud overview, workflow, security notice, AI limitation disclaimer.
  - [ ] Authentication (`/login`, `/register`): Responsive forms, JWT storage, protected routes.
  - [ ] Dashboard (`/dashboard`): Dynamic statistics, risk distribution charts, quick upload, recent analyses.
  - [ ] Upload page (`/upload`): Drag-and-drop, client-side validation, upload progress, direct analysis dispatch.
  - [ ] Document Detail page (`/documents/[id]`): Multi-tab layout (Overview, Extracted Fields, Forensics & ELA Viewer, ML & Risk Breakdown, Audit Log).
  - [ ] History page (`/history`): Filter by risk level, search by filename/student name, pagination, report download.
  - [ ] Settings page (`/settings`): Document retention policies, security options, team credits.

- [ ] **Phase 10: Testing, Quality Assurance & Security Hardening**
  - [ ] Pytest test suites: unit tests for OCR, forensics, field extraction, risk engine, models, and auth.
  - [ ] API integration tests: upload, verification, unauthorized access prevention, data isolation.
  - [ ] Synthetic fixture creation for reliable test runs.

- [ ] **Phase 11: Deployment Configuration & CI/CD**
  - [ ] Dockerfiles for backend and frontend.
  - [ ] Multi-container `docker-compose.yml` (PostgreSQL, Redis, Celery Worker, FastAPI backend, Next.js frontend).
  - [ ] `.env.example` with documented configuration parameters.
  - [ ] GitHub Actions CI workflow for linting and automated test runs.

- [ ] **Phase 12: Final Audit, Verification & Project Documentation**
  - [ ] Comprehensive `README.md` with setup guides, screenshots, command references, and academic credits.
  - [ ] Verification matrix confirming every requirement from the Master Project Prompt.
