"""Rule-based and pattern extractor for academic certificates and mark sheets."""
import re
from typing import Dict, Any, List, Optional
from ai.ocr.engine import OCRPageResult

class AcademicFieldExtractor:
    """Extracts standardized academic entities from OCR text and bounding boxes."""

    # Universal identifier patterns (Roll No, Serial No, Doc ID, Invoice/Cert No)
    ROLL_PATTERNS = [
        r"(?:Roll\s*(?:No|Number)|Registration\s*(?:No|Number)|Enrollment\s*(?:No|Number)|Reg\.\s*No\.?)[:\s\-]+([A-Z0-9\/\-]{4,24})",
        r"(?:Student\s*ID|ID\s*(?:No|Number)|UID|Seat\s*No\.?|Doc\s*ID|Invoice\s*(?:No|#)|Reference\s*No\.?)[:\s\-]+([A-Z0-9\/\-]{4,24})",
        r"(?:Certificate\s*(?:No|Number)|Sr\.\s*No\.?|Serial\s*(?:No|Number))[:\s\-]+([A-Z0-9\/\-]{4,24})"
    ]

    CERTIFICATE_PATTERNS = [
        r"(?:Certificate\s*(?:No|Number)|Sr\.\s*No\.?|Serial\s*(?:No|Number))[:\s\-]+([A-Z0-9\/\-]{4,24})",
        r"(?:Doc\s*Id|Verification\s*Code|Ref\.\s*No)[:\s\-]+([A-Z0-9\/\-]{4,24})"
    ]

    DATE_PATTERNS = [
        r"(?:Date\s*of\s*Issue|Issue\s*Date|Dated|Date|Date\s*of\s*Birth|DOB)[:\s\-]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?:Date\s*of\s*Issue|Issue\s*Date|Dated|Date)[:\s\-]+(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4})",
        r"(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})",
        r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)[\s,]+\d{4})"
    ]

    MARKS_PATTERNS = [
        r"(?:CGPA|Cumulative\s*Grade\s*Point\s*Average)[:\s\-]+([0-9\.]+\s*(?:\/\s*10(?:\.0)?)?)",
        r"(?:Total\s*Marks|Marks\s*Obtained|Percentage|Score)[:\s\-]+([0-9\.]+\s*%(?:\s*out\s*of\s*[0-9]+)?|[0-9\.]+\s*\/\s*[0-9]+)",
        r"(?:Grade|Division|Class)[:\s\-]+(First\s*Class(?:\s*with\s*Distinction)?|Second\s*Class|Pass|Grade\s*[A-O][\+\-]?|[A-O][\+\-]?|Distinction)",
        r"(?:Total\s*Amount|Amount|Balance\s*Due|Net\s*Total)[:\s\-]+([₹\$€£]?\s*[0-9,]+(?:\.[0-9]{2})?)"
    ]

    DEGREE_KEYWORDS = [
        r"(?:Bachelor\s+of\s+[A-Za-z\s]+|Master\s+of\s+[A-Za-z\s]+|Doctor\s+of\s+[A-Za-z\s]+)",
        r"(?:B\.Tech|B\.E\.|B\.Sc|B\.Com|B\.A|BCA|BBA|M\.Tech|M\.E\.|M\.Sc|M\.Com|M\.A|MCA|MBA|Ph\.D)[A-Za-z\s,\.]*",
        r"(?:Diploma\s+in\s+[A-Za-z\s]+|Secondary\s+School\s+Examination|Higher\s+Secondary\s+Certificate)",
        r"(?:Certificate\s+of\s+[A-Za-z\s]+|Training\s+in\s+[A-Za-z\s]+|Completed\s+the\s+Course\s+in\s+[A-Za-z\s]+)"
    ]

    INSTITUTION_KEYWORDS = [
        r"(?:[A-Z][a-zA-Z\s]+(?:University|Institute\s+of\s+Technology|College\s+of\s+Engineering|Vidyapeeth|Academy|Autonomous\s+College|School|Board\s+of\s+Education))",
        r"(?:Indian\s+Institute\s+of\s+[A-Za-z\s]+|National\s+Institute\s+of\s+[A-Za-z\s]+|Government\s+of\s+[A-Za-z\s]+)",
        r"(?:[A-Z][a-zA-Z\s]+(?:Corporation|Services\s+Ltd|Pvt\s+Ltd|Technologies|Enterprises|Solutions))"
    ]

    NAME_PREFIXES = [
        r"(?:This\s+is\s+to\s+certify\s+that|Certify\s+that|Certified\s+that|Name\s*(?:of\s*(?:Student|Candidate|Holder))?[:\s\-]+)\s*([A-Z][a-zA-Z\s\.\']{2,40}?)(?=\s+(?:son\s+of|daughter\s+of|bearing|has\s+completed|having|was\s+awarded|\n|\r|$))",
        r"(?:Awarded\s+to|Conferred\s+upon|Presented\s+to)[:\s\-]*([A-Z][a-zA-Z\s\.\']{2,40})",
        r"(?:Mr\.|Ms\.|Shri|Smt\.|Dr\.)\s+([A-Z][a-zA-Z\s\.\']{2,40})"
    ]

    @classmethod
    def extract_fields(cls, ocr_results: List[OCRPageResult]) -> Dict[str, Dict[str, Any]]:
        """
        Extract academic fields across all pages of the document.
        Returns a dict of fields with keys:
          - field_value: extracted string or None
          - confidence: float score between 0.0 and 1.0
          - bounding_box: coordinates or None
        """
        combined_text = "\n".join([page.text for page in ocr_results])
        all_bboxes = []
        for p in ocr_results:
            all_bboxes.extend(p.bounding_boxes)

        extracted: Dict[str, Dict[str, Any]] = {
            "student_name": {"value": None, "confidence": 0.0, "bounding_box": None},
            "institution_name": {"value": None, "confidence": 0.0, "bounding_box": None},
            "degree_course": {"value": None, "confidence": 0.0, "bounding_box": None},
            "roll_number": {"value": None, "confidence": 0.0, "bounding_box": None},
            "certificate_number": {"value": None, "confidence": 0.0, "bounding_box": None},
            "issue_date": {"value": None, "confidence": 0.0, "bounding_box": None},
            "marks_grade": {"value": None, "confidence": 0.0, "bounding_box": None},
        }

        # 1. Roll / Registration Number
        for pattern in cls.ROLL_PATTERNS:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                extracted["roll_number"] = {
                    "value": val,
                    "confidence": 0.92,
                    "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                }
                break

        # 2. Certificate Number
        for pattern in cls.CERTIFICATE_PATTERNS:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                extracted["certificate_number"] = {
                    "value": val,
                    "confidence": 0.88,
                    "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                }
                break

        # 3. Issue Date
        for pattern in cls.DATE_PATTERNS:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                extracted["issue_date"] = {
                    "value": val,
                    "confidence": 0.85,
                    "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                }
                break

        # 4. Marks / Grade / CGPA
        for pattern in cls.MARKS_PATTERNS:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                extracted["marks_grade"] = {
                    "value": val,
                    "confidence": 0.86,
                    "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                }
                break

        # 5. Degree / Course
        for pattern in cls.DEGREE_KEYWORDS:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val = match.group(0).strip().rstrip(",.")
                extracted["degree_course"] = {
                    "value": val,
                    "confidence": 0.84,
                    "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                }
                break

        # 6. Institution Name
        for pattern in cls.INSTITUTION_KEYWORDS:
            match = re.search(pattern, combined_text)
            if match:
                val = match.group(0).strip().rstrip(",.")
                extracted["institution_name"] = {
                    "value": val,
                    "confidence": 0.87,
                    "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                }
                break

        # 7. Student Name
        for pattern in cls.NAME_PREFIXES:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if len(val.split()) >= 1 and len(val) < 45:
                    extracted["student_name"] = {
                        "value": val,
                        "confidence": 0.80,
                        "bounding_box": cls._find_matching_bbox(val, all_bboxes)
                    }
                    break

        return extracted

    @staticmethod
    def _find_matching_bbox(query: str, bboxes: List[Dict[str, Any]]) -> Optional[List[float]]:
        """Find the bounding box of a detected text token."""
        if not query or not bboxes:
            return None
        q_clean = query.lower()
        for b in bboxes:
            text = b.get("text", "").lower()
            if q_clean in text or text in q_clean:
                return b.get("bbox")
        return None
