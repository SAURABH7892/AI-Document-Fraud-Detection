# DocShield AI — Security & Privacy Architecture

## 1. Authentication & Session Management
- **Password Storage:** Uses strong salt-hashed bcrypt (12 rounds) storage. Plaintext passwords are never logged or stored.
- **Tokens:** Short-lived JSON Web Tokens (JWT) signed via HMAC-SHA256 (`HS256`).
- **Token Invalidation:** Client-side token flush and server-side authorization dependency validation.

---

## 2. Authorization & Resource Ownership Isolation
- **Ownership Verification:** Every database query targeting documents (`/documents/{id}`, `/verifications/{id}`, `/verifications/{id}/report`) explicitly verifies that the requested resource's `user_id` matches the authenticated `current_user.id`.
- **Cross-User Protection:** If User B attempts to access a document uploaded by User A, the server returns `404 Not Found` or `403 Forbidden`, preventing unauthorized data discovery.

---

## 3. Server-Side File Validation Pipeline
1. **Filename Sanitization:** Path traversal sequences (`../`, `..\\`) are stripped.
2. **File Size Enforcement:** Uploads strictly capped at 15 MB.
3. **MIME & Extension Whitelisting:** Restricted to `.pdf`, `.jpg`, `.jpeg`, `.png`.
4. **Magic Byte Signature Inspection:** Upload bytes are checked against real binary signatures (`%PDF-`, `\xFF\xD8\xFF`, `\x89PNG\r\n\x1a\n`). Files with spoofed extensions (e.g. executable renamed to `.pdf`) are immediately rejected.
5. **Cryptographic Checksum:** SHA-256 digest computed at ingress and permanently embedded in verification records and reports.

---

## 4. Privacy & Document Retention
- **Per-Document UUID Storage:** Files are stored in per-document isolated paths (`storage/uploads/{uuid}/`).
- **User-Initiated Deletion:** Deleting a document completely deletes the source file, generated ELA visual artifacts, and PDF reports from physical storage.
- **Untrusted Content Handling:** Uploaded documents are treated as passive binary assets; no macros, active PDF scripts, or embedded instructions are executed.
