"""Standardized feature vector schema for ML training and inference."""
from typing import Dict, Any, List
import numpy as np

FEATURE_NAMES = [
    "ocr_confidence_avg",
    "ocr_word_count",
    "ocr_char_density",
    "ela_mean_error",
    "ela_std_error",
    "ela_max_error",
    "ela_cluster_count",
    "noise_median_var",
    "noise_iqr_var",
    "noise_inconsistency_index",
    "layout_height_variance",
    "layout_slope_variance",
    "edge_density",
    "meta_suspicious_producer",
    "meta_timestamp_anomaly",
    "extracted_field_count",
    "field_confidence_avg",
    "is_pdf"
]

def build_feature_dict(
    ocr_results: List[Any],
    forensic_features: Dict[str, float],
    extracted_fields: Dict[str, Any],
    mime_type: str,
    page_count: int = 1
) -> Dict[str, float]:
    """
    Construct standardized numerical feature dictionary from analysis components.
    Guarantees no missing features and consistent data types.
    """
    # 1. OCR metrics
    if ocr_results:
        ocr_conf = float(np.mean([r.confidence_avg for r in ocr_results]))
        word_count = float(sum([r.word_count for r in ocr_results]))
        total_text_len = sum([len(r.text) for r in ocr_results])
        char_density = float(total_text_len) / max(1.0, float(page_count * 2000))
    else:
        ocr_conf = 0.0
        word_count = 0.0
        char_density = 0.0

    # 2. Extracted fields metrics
    field_count = 0
    field_confs = []
    for k, v in extracted_fields.items():
        if isinstance(v, dict) and v.get("value") is not None:
            field_count += 1
            field_confs.append(v.get("confidence", 0.0))
    avg_field_conf = float(np.mean(field_confs)) if field_confs else 0.0

    # 3. Assemble complete feature vector matching FEATURE_NAMES
    features = {
        "ocr_confidence_avg": float(ocr_conf),
        "ocr_word_count": float(word_count),
        "ocr_char_density": float(char_density),
        "ela_mean_error": float(forensic_features.get("ela_mean_error", 0.0)),
        "ela_std_error": float(forensic_features.get("ela_std_error", 0.0)),
        "ela_max_error": float(forensic_features.get("ela_max_error", 0.0)),
        "ela_cluster_count": float(forensic_features.get("ela_cluster_count", 0.0)),
        "noise_median_var": float(forensic_features.get("noise_median_var", 0.0)),
        "noise_iqr_var": float(forensic_features.get("noise_iqr_var", 0.0)),
        "noise_inconsistency_index": float(forensic_features.get("noise_inconsistency_index", 0.0)),
        "layout_height_variance": float(forensic_features.get("layout_height_variance", 0.0)),
        "layout_slope_variance": float(forensic_features.get("layout_slope_variance", 0.0)),
        "edge_density": float(forensic_features.get("edge_density", 0.0)),
        "meta_suspicious_producer": float(forensic_features.get("meta_suspicious_producer", 0.0)),
        "meta_timestamp_anomaly": float(forensic_features.get("meta_timestamp_anomaly", 0.0)),
        "extracted_field_count": float(field_count),
        "field_confidence_avg": float(avg_field_conf),
        "is_pdf": 1.0 if mime_type == "application/pdf" else 0.0
    }

    return features

def vector_from_feature_dict(feat_dict: Dict[str, float]) -> List[float]:
    """Convert feature dictionary to ordered feature vector."""
    return [float(feat_dict.get(name, 0.0)) for name in FEATURE_NAMES]
