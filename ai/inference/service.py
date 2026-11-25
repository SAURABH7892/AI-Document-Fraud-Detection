"""ML inference service with graceful degradation and truthful availability checks."""
import os
import json
import logging
from typing import Dict, Any, Optional
import numpy as np
from backend.app.core.config import settings
from ai.features.schema import FEATURE_NAMES, vector_from_feature_dict

logger = logging.getLogger(__name__)

class MLInferenceService:
    """Performs inference using trained scikit-learn/XGBoost models."""

    _model = None
    _metadata = None
    _loaded = False

    @classmethod
    def load_model(cls) -> bool:
        """Attempt to load model artifact and metadata."""
        if cls._loaded:
            return cls._model is not None

        model_path = os.path.abspath(settings.ML_MODEL_PATH)
        metadata_path = os.path.join(os.path.dirname(model_path), "model_metadata.json")

        if not os.path.exists(model_path):
            logger.info(f"Model artifact not found at {model_path}. Inference service running in inactive/untrained mode.")
            cls._loaded = True
            cls._model = None
            return False

        try:
            import joblib
            cls._model = joblib.load(model_path)
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    cls._metadata = json.load(f)
            else:
                cls._metadata = {"model_name": "DocShield-Classifier", "version": "1.0.0"}
            cls._loaded = True
            logger.info(f"Successfully loaded model artifact from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load ML model artifact: {e}")
            cls._loaded = True
            cls._model = None
            return False

    @classmethod
    def predict(cls, feature_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Run inference on feature dictionary.
        Returns truthful prediction response.
        """
        cls.load_model()

        if cls._model is None:
            return {
                "is_available": False,
                "model_name": "DocShield-ML-Classifier",
                "model_version": "N/A",
                "prediction_label": "Model not trained / unavailable",
                "fraud_probability": None,
                "feature_vector": feature_dict,
                "explanation": "No trained model artifact is currently deployed. Heuristic and forensic signals will be utilized exclusively."
            }

        try:
            features_vec = np.array([vector_from_feature_dict(feature_dict)])
            
            # Predict probability if supported
            if hasattr(cls._model, "predict_proba"):
                probs = cls._model.predict_proba(features_vec)[0]
                # Class 1 is TAMPERED/FRAUD
                fraud_prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
            else:
                pred = cls._model.predict(features_vec)[0]
                fraud_prob = 1.0 if pred == 1 else 0.0

            if fraud_prob >= 0.70:
                label = "TAMPERED"
            elif fraud_prob >= 0.40:
                label = "SUSPICIOUS"
            else:
                label = "AUTHENTIC"

            return {
                "is_available": True,
                "model_name": cls._metadata.get("model_name", "RandomForestClassifier") if cls._metadata else "RandomForestClassifier",
                "model_version": cls._metadata.get("version", "1.0.0") if cls._metadata else "1.0.0",
                "prediction_label": label,
                "fraud_probability": round(fraud_prob, 3),
                "feature_vector": feature_dict,
                "explanation": f"Model assessed fraud probability at {fraud_prob*100:.1f}% based on multi-signal feature vector."
            }
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return {
                "is_available": False,
                "model_name": "DocShield-ML-Classifier",
                "model_version": "Error",
                "prediction_label": "Inference Error",
                "fraud_probability": None,
                "feature_vector": feature_dict,
                "explanation": f"Error during model inference: {str(e)}"
            }
