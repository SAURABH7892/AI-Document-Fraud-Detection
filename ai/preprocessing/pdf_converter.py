"""PDF page rendering and document image normalization."""
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
from typing import List, Tuple, Dict, Any

class DocumentPreprocessor:
    """Handles PDF rendering and image normalization for OCR and forensics."""

    @staticmethod
    def render_pdf_to_images(pdf_path: str, dpi: int = 200) -> List[np.ndarray]:
        """Render all pages of a PDF into RGB numpy image arrays."""
        doc = fitz.open(pdf_path)
        page_images = []
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_images.append(np.array(img))

        doc.close()
        return page_images

    @staticmethod
    def load_document_images(file_path: str, mime_type: str) -> List[np.ndarray]:
        """Load document pages whether it is a PDF or raster image."""
        if mime_type == "application/pdf":
            return DocumentPreprocessor.render_pdf_to_images(file_path)
        else:
            # JPG or PNG image
            img = cv2.imread(file_path)
            if img is None:
                pil_img = Image.open(file_path).convert("RGB")
                img = np.array(pil_img)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return [img]

    @staticmethod
    def extract_pdf_metadata(pdf_path: str) -> Dict[str, Any]:
        """Extract internal metadata dictionary and page count from PDF."""
        metadata = {
            "page_count": 1,
            "producer": None,
            "creator": None,
            "creation_date": None,
            "mod_date": None,
            "is_encrypted": False,
            "has_incremental_updates": False
        }
        try:
            doc = fitz.open(pdf_path)
            metadata["page_count"] = len(doc)
            metadata["is_encrypted"] = doc.is_encrypted
            doc_meta = doc.metadata or {}
            metadata["producer"] = doc_meta.get("producer")
            metadata["creator"] = doc_meta.get("creator")
            metadata["creation_date"] = doc_meta.get("creationDate")
            metadata["mod_date"] = doc_meta.get("modDate")
            doc.close()
        except Exception:
            pass
        return metadata

    @staticmethod
    def enhance_for_ocr(image: np.ndarray) -> np.ndarray:
        """Apply grayscale conversion, mild denoising and contrast enhancement."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()
        # Mild unsharp masking or adaptive thresholding
        denoised = cv2.fastNlMeansDenoising(gray, h=7)
        return denoised
