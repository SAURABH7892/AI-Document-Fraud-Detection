"""Synthetic academic certificate feature dataset generator."""
import os
import json
import random
import numpy as np
from typing import List, Dict, Any
from ai.features.schema import FEATURE_NAMES

def generate_synthetic_dataset(num_samples: int = 200, output_path: str = "ai/training/synthetic_dataset.json") -> str:
    """
    Generate synthetic authentic and tampered academic document feature vectors.
    Uses grouped document IDs so authentic base templates and their tampered counterparts
    remain in the same split to prevent data leakage.
    """
    random.seed(42)
    np.random.seed(42)

    data = []
    num_groups = num_samples // 4

    for group_id in range(num_groups):
        # Base template characteristics for this university
        base_word_count = int(np.random.normal(120, 20))
        base_char_density = float(np.random.normal(0.45, 0.05))
        base_edge_density = float(np.random.normal(0.04, 0.01))
        
        # 1. Authentic variant (2 samples per group)
        for _ in range(2):
            feat = {
                "group_id": f"group_{group_id}",
                "label": 0,  # 0 = AUTHENTIC
                "ocr_confidence_avg": float(np.clip(np.random.normal(0.96, 0.02), 0.88, 0.99)),
                "ocr_word_count": float(base_word_count + np.random.randint(-5, 5)),
                "ocr_char_density": float(np.clip(base_char_density + np.random.normal(0, 0.02), 0.2, 0.8)),
                "ela_mean_error": float(np.clip(np.random.normal(2.5, 0.5), 0.5, 5.0)),
                "ela_std_error": float(np.clip(np.random.normal(4.8, 1.2), 1.0, 9.5)),
                "ela_max_error": float(np.clip(np.random.normal(35.0, 8.0), 15.0, 65.0)),
                "ela_cluster_count": float(np.random.choice([0, 1], p=[0.85, 0.15])),
                "noise_median_var": float(np.clip(np.random.normal(45.0, 8.0), 20.0, 80.0)),
                "noise_iqr_var": float(np.clip(np.random.normal(12.0, 3.0), 4.0, 25.0)),
                "noise_inconsistency_index": float(np.clip(np.random.normal(1.2, 0.3), 0.5, 2.2)),
                "layout_height_variance": float(np.clip(np.random.normal(0.45, 0.1), 0.2, 0.85)),
                "layout_slope_variance": float(np.clip(np.random.normal(0.005, 0.002), 0.001, 0.015)),
                "edge_density": float(np.clip(base_edge_density + np.random.normal(0, 0.005), 0.01, 0.1)),
                "meta_suspicious_producer": 0.0,
                "meta_timestamp_anomaly": 0.0,
                "extracted_field_count": float(np.random.choice([5, 6, 7], p=[0.2, 0.5, 0.3])),
                "field_confidence_avg": float(np.clip(np.random.normal(0.89, 0.04), 0.75, 0.98)),
                "is_pdf": 1.0
            }
            data.append(feat)

        # 2. Tampered variant (2 samples per group: altered grades, spliced names, modified roll numbers)
        for _ in range(2):
            feat = {
                "group_id": f"group_{group_id}",
                "label": 1,  # 1 = TAMPERED
                "ocr_confidence_avg": float(np.clip(np.random.normal(0.82, 0.08), 0.55, 0.95)),
                "ocr_word_count": float(base_word_count + np.random.randint(-15, 15)),
                "ocr_char_density": float(np.clip(base_char_density + np.random.normal(0, 0.06), 0.2, 0.8)),
                "ela_mean_error": float(np.clip(np.random.normal(7.8, 1.8), 4.0, 15.0)),
                "ela_std_error": float(np.clip(np.random.normal(16.5, 3.5), 10.5, 28.0)),
                "ela_max_error": float(np.clip(np.random.normal(92.0, 20.0), 55.0, 160.0)),
                "ela_cluster_count": float(np.random.choice([3, 4, 5, 6], p=[0.2, 0.4, 0.25, 0.15])),
                "noise_median_var": float(np.clip(np.random.normal(75.0, 18.0), 35.0, 130.0)),
                "noise_iqr_var": float(np.clip(np.random.normal(48.0, 12.0), 25.0, 85.0)),
                "noise_inconsistency_index": float(np.clip(np.random.normal(4.2, 0.9), 2.9, 7.5)),
                "layout_height_variance": float(np.clip(np.random.normal(1.4, 0.3), 0.95, 2.4)),
                "layout_slope_variance": float(np.clip(np.random.normal(0.04, 0.015), 0.02, 0.08)),
                "edge_density": float(np.clip(base_edge_density * 1.5 + np.random.normal(0, 0.01), 0.03, 0.15)),
                "meta_suspicious_producer": float(np.random.choice([0.0, 1.0], p=[0.4, 0.6])),
                "meta_timestamp_anomaly": float(np.random.choice([0.0, 1.0], p=[0.6, 0.4])),
                "extracted_field_count": float(np.random.choice([3, 4, 5], p=[0.3, 0.4, 0.3])),
                "field_confidence_avg": float(np.clip(np.random.normal(0.68, 0.09), 0.45, 0.82)),
                "is_pdf": 1.0
            }
            data.append(feat)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    return output_path

if __name__ == "__main__":
    path = generate_synthetic_dataset()
    print(f"Generated synthetic dataset at: {path}")
