"""Server-side file validation and security inspection."""
import hashlib
from typing import Tuple

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_MIMES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png"
}

# Magic byte signatures
MAGIC_BYTES = {
    b"%PDF": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png"
}

class FileValidationError(Exception):
    """Raised when file validation fails."""
    pass

def validate_uploaded_file(filename: str, content: bytes, content_type: str = None) -> Tuple[str, str, int, str]:
    """
    Validate uploaded file for extension, size, magic signature, and hash.
    Returns: (detected_extension, verified_mime, file_size, sha256_hash)
    """
    if not filename:
        raise FileValidationError("Filename cannot be empty.")

    # 1. Check size
    file_size = len(content)
    if file_size == 0:
        raise FileValidationError("Uploaded file is empty (0 bytes).")
    if file_size > MAX_FILE_SIZE:
        raise FileValidationError(f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE // (1024*1024)} MB.")

    # 2. Check extension
    import os
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # 3. Check magic byte signature
    verified_mime = None
    for signature, mime in MAGIC_BYTES.items():
        if content.startswith(signature):
            verified_mime = mime
            break

    if not verified_mime:
        raise FileValidationError("File signature verification failed. The file header does not match a valid PDF, JPEG, or PNG.")

    # 4. Check consistency between extension and signature
    if ext == ".pdf" and verified_mime != "application/pdf":
        raise FileValidationError("File extension '.pdf' does not match file content signature.")
    if ext in {".jpg", ".jpeg"} and verified_mime != "image/jpeg":
        raise FileValidationError(f"File extension '{ext}' does not match JPEG signature.")
    if ext == ".png" and verified_mime != "image/png":
        raise FileValidationError("File extension '.png' does not match PNG signature.")

    # 5. Compute SHA-256 digest
    sha256_hash = hashlib.sha256(content).hexdigest()

    return ext, verified_mime, file_size, sha256_hash
