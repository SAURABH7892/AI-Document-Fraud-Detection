"""Test script to upload a sample Government ID and verify DigiLocker integration end-to-end."""
import io
import time
import json
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_aadhaar_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 720, "GOVERNMENT OF INDIA")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "Unique Identification Authority of India (UIDAI)")
    c.drawString(100, 660, "To: Priya Sharma")
    c.drawString(100, 640, "Address: 42, Civil Lines, New Delhi, Delhi - 110001")
    c.drawString(100, 610, "DOB: 12/06/1996")
    c.drawString(100, 590, "Gender: Female")
    c.setFont("Helvetica-Bold", 16)
    # Valid 12-digit Aadhaar number with valid Verhoeff check digit (367598342515)
    c.drawString(100, 550, "3675 9834 2515")
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(100, 520, "Mera Aadhaar, Meri Pehchan")
    c.save()
    return buf.getvalue()

def run_test():
    # 1. Login
    login_data = json.dumps({"email": "demo@docshield.ai", "password": "DemoPass123!"}).encode()
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    token = json.loads(res.read())["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Aadhaar PDF
    pdf_bytes = create_sample_aadhaar_pdf()
    boundary = "----DocShieldBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="priya_aadhaar_card.pdf"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode() + pdf_bytes + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"document_type\"\r\n\r\ngovernment_id\r\n--{boundary}--\r\n".encode()

    upload_req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/documents",
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    up_res = urllib.request.urlopen(upload_req)
    doc_id = json.loads(up_res.read())["id"]
    print("Uploaded Document ID:", doc_id)

    # 3. Wait for background verification
    completed = False
    for i in range(30):
        time.sleep(0.5)
        job_req = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/documents/{doc_id}/job", headers=headers)
        job_res = urllib.request.urlopen(job_req)
        status_data = json.loads(job_res.read())
        if status_data.get("status") == "COMPLETED":
            completed = True
            break
        elif status_data.get("status") == "FAILED":
            print("Job Failed:", status_data)
            return

    if not completed:
        print("Timeout waiting for job completion.")
        return

    # 4. Fetch verification details
    v_req = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/verifications/by-document/{doc_id}", headers=headers)
    v_res = urllib.request.urlopen(v_req)
    v_data = json.loads(v_res.read())

    print("\n=== Verification Summary ===")
    print("Risk Level:", v_data.get("risk_level"))
    print("Risk Score:", v_data.get("risk_score"))
    print("Issuer Status:", v_data.get("issuer_verification_status"))
    print("Recommendation:", v_data.get("recommendation"))
    
    meta = v_data.get("issuer_metadata")
    if meta:
        print("\n=== DigiLocker Government ID Metadata ===")
        print("Is Gov ID:", meta.get("is_gov_id"))
        print("ID Type:", meta.get("id_type_label"))
        print("Masked ID:", meta.get("id_number_masked"))
        print("Authority:", meta.get("authority"))
        print("Checksum Valid:", meta.get("checksum_valid"), f"({meta.get('checksum_details')})")
        print("Transaction ID:", meta.get("transaction_id"))
        print("Status Text:", meta.get("status_text"))

    # 5. Download and verify PDF report
    rep_req = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/verifications/documents/{doc_id}/report?token={token}")
    rep_res = urllib.request.urlopen(rep_req)
    rep_bytes = rep_res.read()
    print("\nReport Download Success! Size:", len(rep_bytes), "bytes. Header:", rep_bytes[:8])

if __name__ == "__main__":
    run_test()
