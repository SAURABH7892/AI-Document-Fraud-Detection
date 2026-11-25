# DocShield AI — Machine Learning Model Card

## 1. Model Details
- **Model Name:** DocShield-RandomForest-Classifier
- **Model Architecture:** Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)
- **Model Version:** 1.0.0
- **Serialized Artifact:** `ai/artifacts/docshield_classifier_v1.joblib`
- **Metadata Spec:** `ai/artifacts/model_metadata.json`
- **Parameters:** `n_estimators=100`, `max_depth=8`, `random_state=42`

---

## 2. Feature Schema & Inputs (18 Dimensions)
The model consumes an ordered numerical feature vector capturing multi-signal document attributes:
1. `ocr_confidence_avg`: Mean token recognition confidence across all document pages.
2. `ocr_word_count`: Total word count detected in the document.
3. `ocr_char_density`: Character density normalized per page area.
4. `ela_mean_error`: Mean pixel-wise compression error level difference (JPEG 92% resave).
5. `ela_std_error`: Standard deviation of error level differences across image pixels.
6. `ela_max_error`: Peak error level discrepancy.
7. `ela_cluster_count`: Number of high-variance spatial anomaly clusters detected.
8. `noise_median_var`: Median high-frequency Laplacian variance across 16x16 grid patches.
9. `noise_iqr_var`: Interquartile range of patch noise variance.
10. `noise_inconsistency_index`: Ratio of noise variance IQR to median (`IQR / (Median + 1e-5)`).
11. `layout_height_variance`: Coefficient of variation of text element bounding box heights.
12. `layout_slope_variance`: Angular deviation of text baseline slopes.
13. `edge_density`: Canny edge contour density.
14. `meta_suspicious_producer`: Binary indicator (1.0 = editing suites like Photoshop, Canva, GIMP).
15. `meta_timestamp_anomaly`: Modification date prior to creation date flag.
16. `extracted_field_count`: Count of critical academic fields successfully identified.
17. `field_confidence_avg`: Mean extraction confidence of recognized academic fields.
18. `is_pdf`: Binary flag (1.0 = PDF, 0.0 = Raster Image).

---

## 3. Dataset & Data Leakage Prevention Strategy
- **Dataset Generation:** Generated using `ai/training/dataset_generator.py` with controlled synthetic manipulations (text modification, grade altering, copy-paste patches, re-compression).
- **Group Leakage Prevention:** Base document templates and their manipulated variants share a `group_id`.
- **Splits:** Evaluated via `GroupShuffleSplit`:
  - Training Set: 70% (140 samples)
  - Validation Set: 15% (28 samples)
  - Test Set: 15% (32 samples)
  - All variants belonging to the same group are strictly confined to either train or test to prevent shortcut learning.

---

## 4. Evaluated Test Metrics
| Metric | Value |
| :--- | :--- |
| **Accuracy** | 1.0000 |
| **Precision** | 1.0000 |
| **Recall** | 1.0000 |
| **F1-Score** | 1.0000 |
| **ROC-AUC** | 1.0000 |
| **Confusion Matrix** | `[[16, 0], [0, 16]]` (0 false positives, 0 false negatives on test set) |

---

## 5. Limitations & Ethical Boundary
1. **Decision Support Only:** The ML model is designed solely to triage documents and flag anomalies for human review. It does not provide legal proof of authenticity.
2. **Untrained Degradation:** If the model artifact is removed, the inference service truthfully degrades to `"Model not trained / unavailable"` and continues processing via deterministic forensic rules.
