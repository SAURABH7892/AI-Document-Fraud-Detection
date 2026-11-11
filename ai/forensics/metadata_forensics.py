"""Pillar 1: Deep metadata, font structure, and PDF container forensics."""
import re
from typing import Dict, Any, List

class DeepMetadataForensics:
    """Inspects container structure, incremental updates, font subsets, and software footprints."""

    SUSPICIOUS_PRODUCERS = [
        "photoshop", "gimp", "canva", "coreldraw", "illustrator",
        "paint.net", "inkscape", "pdfescape", "ilovepdf", "sejda"
    ]

    ENTERPRISE_ENGINES = [
        "itext", "jasperreports", "reportlab", "oracle", "prawn",
        "apache fop", "pdfbox", "quartz", "cairo", "afp"
    ]

    @classmethod
    def analyze_pdf_structure(cls, pdf_path: str, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep inspection of PDF container:
        1. Multi-revision trailer detection (incremental editing via %%EOF count).
        2. Embedded font consistency.
        3. Stripped metadata indicators.
        4. Desktop editing suite footprints.
        """
        findings = []
        features = {}

        # 1. Inspect Raw File for Incremental Updates (%%EOF count)
        eof_count = 0
        try:
            with open(pdf_path, "rb") as f:
                content = f.read()
                # Count occurrences of %%EOF which indicates appended revisions
                eof_count = len(re.findall(b"%%EOF", content))
        except Exception:
            eof_count = 1

        has_incremental_alteration = eof_count > 1
        features["meta_incremental_revisions"] = float(eof_count)

        if has_incremental_alteration:
            findings.append({
                "signal": "incremental_pdf_updates",
                "severity": "HIGH",
                "category": "ALTERATION",
                "finding": f"Detected {eof_count} appended revision trailers (%%EOF markers). Indicates document was modified and re-saved after initial creation."
            })

        # 2. Producer / Creator Signature Analysis
        producer = str(raw_metadata.get("producer") or "").lower()
        creator = str(raw_metadata.get("creator") or "").lower()
        combined = f"{producer} {creator}"

        suspicious_matches = [tool for tool in cls.SUSPICIOUS_PRODUCERS if tool in combined]
        features["meta_suspicious_editor"] = 1.0 if suspicious_matches else 0.0

        if suspicious_matches:
            findings.append({
                "signal": "desktop_editing_suite",
                "severity": "HIGH",
                "category": "COUNTERFEITING",
                "finding": f"Software signature identifies interactive design editor: '{', '.join(suspicious_matches)}'."
            })

        # 3. Stripped / Missing Metadata Check
        is_stripped = not producer and not creator and not raw_metadata.get("creation_date")
        features["meta_stripped_exif"] = 1.0 if is_stripped else 0.0

        if is_stripped:
            findings.append({
                "signal": "stripped_metadata",
                "severity": "MEDIUM",
                "category": "COUNTERFEITING",
                "finding": "Document metadata (CreationDate, Producer, Author) completely stripped or sanitized."
            })

        # 4. Font Subset Consistency Analysis via PyMuPDF
        font_inconsistency = False
        try:
            import fitz
            doc = fitz.open(pdf_path)
            font_names = []
            for page in doc:
                fonts = page.get_fonts()
                for f in fonts:
                    font_names.append(f[3]) # font family name
            doc.close()

            # Check if document mixes tagged subsets (e.g. ABCDE+Arial) with loose system fonts
            subset_fonts = [fn for fn in font_names if "+" in fn]
            non_subset_fonts = [fn for fn in font_names if "+" not in fn]
            
            if subset_fonts and non_subset_fonts and len(font_names) > 3:
                font_inconsistency = True
                findings.append({
                    "signal": "font_structure_inconsistency",
                    "severity": "MEDIUM",
                    "category": "ALTERATION",
                    "finding": f"Document mixes embedded subset fonts ({len(subset_fonts)}) with untagged system fonts ({len(non_subset_fonts)}). Common indicator of secondary text insertion."
                })
        except Exception:
            pass

        features["meta_font_inconsistency"] = 1.0 if font_inconsistency else 0.0

        return {
            "findings": findings,
            "features": features,
            "revision_count": eof_count
        }
