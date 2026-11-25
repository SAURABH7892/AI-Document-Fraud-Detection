"""ML Training and Evaluation Pipeline for DocShield AI."""
import os
import json
import joblib
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
from ai.features.schema import FEATURE_NAMES
from ai.training.dataset_generator import generate_synthetic_dataset

def train_and_evaluate(dataset_path: str = "ai/training/synthetic_dataset.json"):
    """
    Train Random Forest and Gradient Boosting baseline models with GroupShuffleSplit
    to prevent document template leakage.
    """
    if not os.path.exists(dataset_path):
        dataset_path = generate_synthetic_dataset()

    with open(dataset_path, "r") as f:
        data = json.load(f)

    # Extract X, y, groups
    X = []
    y = []
    groups = []

    for item in data:
        row = [float(item[col]) for col in FEATURE_NAMES]
        X.append(row)
        y.append(int(item["label"]))
        groups.append(str(item["group_id"]))

    X = np.array(X)
    y = np.array(y)
    groups = np.array(groups)

    # Split: 70% Train, 30% Temp (15% Val, 15% Test)
    gss = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
    train_idx, temp_idx = next(gss.split(X, y, groups))

    X_train, y_train, groups_train = X[train_idx], y[train_idx], groups[train_idx]
    X_temp, y_temp, groups_temp = X[temp_idx], y[temp_idx], groups[temp_idx]

    # Split Temp into 50% Val, 50% Test (15% each of total)
    gss_val = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=42)
    val_idx, test_idx = next(gss_val.split(X_temp, y_temp, groups_temp))

    X_val, y_val = X_temp[val_idx], y_temp[val_idx]
    X_test, y_test = X_temp[test_idx], y_temp[test_idx]

    print(f"Dataset split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    # 1. Train Random Forest Baseline
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)

    # Evaluate on Test Set
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print(f"Evaluation Metrics (Random Forest):")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {roc_auc:.4f}")
    print(f"  Confusion Matrix: {cm}")

    # Feature importances
    importances = dict(zip(FEATURE_NAMES, [round(float(v), 4) for v in rf.feature_importances_]))

    # Save artifacts
    artifacts_dir = "ai/artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    model_path = os.path.join(artifacts_dir, "docshield_classifier_v1.joblib")
    joblib.dump(rf, model_path)

    metadata = {
        "model_name": "DocShield-RandomForest-Classifier",
        "version": "1.0.0",
        "algorithm": "RandomForestClassifier",
        "parameters": {"n_estimators": 100, "max_depth": 8, "random_state": 42},
        "dataset_split": {"train": len(X_train), "val": len(X_val), "test": len(X_test)},
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": cm
        },
        "feature_importances": importances,
        "feature_schema": FEATURE_NAMES
    }

    metadata_path = os.path.join(artifacts_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model artifact saved to: {model_path}")
    print(f"Metadata saved to: {metadata_path}")
    return metadata

if __name__ == "__main__":
    train_and_evaluate()
