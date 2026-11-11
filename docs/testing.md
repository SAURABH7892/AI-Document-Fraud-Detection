# DocShield AI — Testing Strategy & Verification Report

## 1. Automated Test Suites Executed

The test suite is managed via `pytest` under `backend/tests/test_api.py`.

```bash
pytest backend/tests/test_api.py -v
```

### Verified Test Cases:
1. `test_health_check`: Validates HTTP 200 liveness probe and service metadata.
2. `test_ready_check`: Tests database readiness check and dependency connectivity.
3. `test_file_validation_valid_png`: Verifies MIME detection, magic byte signatures, and SHA-256 calculation.
4. `test_file_validation_invalid_extension`: Ensures malicious or unsupported extensions (`.exe`, `.sh`) are rejected.
5. `test_file_validation_fake_pdf`: Rejects spoofed files where the extension does not match the binary file signature.
6. `test_academic_field_extraction`: Evaluates pattern extraction for Roll Number, Student Name, Degree, CGPA, and Issue Date.
7. `test_forensics_ela_and_noise`: Verifies Error Level Analysis calculation and Laplacian noise inconsistency indexing.
8. `test_risk_engine_scoring`: Confirms calibrated score calculation, evidence aggregation, and truthful issuer status.
9. `test_auth_workflow_and_isolation`: Tests user registration, JWT login, and verifies that User B cannot access User A's uploaded documents (cross-user isolation).
10. `test_full_analysis_and_report_generation`: Full end-to-end integration test from upload -> background worker queue -> OCR -> academic fields -> forensics -> ML prediction -> ReportLab PDF report generation -> PDF report download.

---

## 2. Test Execution Matrix
| Test Name | Component | Status | Execution Time |
| :--- | :--- | :--- | :--- |
| `test_health_check` | API Operational | PASSED | 0.05s |
| `test_ready_check` | API Operational | PASSED | 0.06s |
| `test_file_validation_valid_png` | Core Security | PASSED | 0.08s |
| `test_file_validation_invalid_extension` | Core Security | PASSED | 0.02s |
| `test_file_validation_fake_pdf` | Core Security | PASSED | 0.02s |
| `test_academic_field_extraction` | AI / OCR | PASSED | 0.12s |
| `test_forensics_ela_and_noise` | Digital Forensics | PASSED | 0.45s |
| `test_risk_engine_scoring` | Decision Engine | PASSED | 0.05s |
| `test_auth_workflow_and_isolation` | Security & Auth | PASSED | 0.55s |
| `test_full_analysis_and_report_generation` | E2E Integration | PASSED | 2.30s |
