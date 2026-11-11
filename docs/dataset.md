# DocShield AI — Dataset Preparation & Synthesis Strategy

## 1. Dataset Ethics & Licensing
In strict accordance with privacy regulations and academic ethics:
- No private, confidential, or sensitive personal student documents were mined or collected without permission.
- The machine learning model was trained using non-sensitive synthetic academic certificate templates with programmatic, controlled manipulations.

---

## 2. Synthetic Tampering Types Implemented
The training pipeline reproduces the most common digital document forgery attacks:
1. **Grade & Marks Modification:** Number replacement with differing typography, baseline elevation, or subtle anti-aliasing artifacts.
2. **Student & Institution Name Splicing:** Pasting names with divergent compression quality levels, causing distinct Error Level Analysis (ELA) signatures.
3. **Typography & Layout Displacement:** Modifying roll number coordinates, creating angular baseline variance and line-height anomalies.
4. **Compression Artifact Inconsistencies:** Saving modified patches across multiple lossy compression iterations, producing localized 8x8 block boundary discontinuities.
5. **Metadata Injections:** Altering document creation and producer strings to reflect image editing tools (e.g., Photoshop, Canva, GIMP).

---

## 3. Data Leakage Prevention (Group Splitting)
A common pitfall in document fraud detection is data leakage, where authentic and tampered versions of the exact same underlying template appear in both the training and test sets. When this occurs, the model merely memorizes the institution's layout rather than forensic tampering signals.

DocShield AI prevents data leakage by:
- Tagging all variants generated from a common base template with a shared `group_id`.
- Utilizing `GroupShuffleSplit` (`sklearn.model_selection.GroupShuffleSplit`) to strictly partition groups into:
  - 70% Training
  - 15% Validation
  - 15% Test
- No group appears in both train and test partitions.
