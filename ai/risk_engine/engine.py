"""Explainable multi-signal risk scoring and decision aggregation engine."""
from typing import List, Dict, Any, Optional
from ai.forensics.analyzer import ForensicFinding

class RiskAssessment:
    def __init__(
        self,
        risk_level: str,
        risk_score: float,
        summary_evidence: List[Dict[str, Any]],
        issuer_verification_status: str,
        recommendation: str
    ):
        self.risk_level = risk_level  # LOW_RISK, MEDIUM_RISK, HIGH_RISK, INCONCLUSIVE
        self.risk_score = round(risk_score, 1)
        self.summary_evidence = summary_evidence
        self.issuer_verification_status = issuer_verification_status
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "summary_evidence": self.summary_evidence,
            "issuer_verification_status": self.issuer_verification_status,
            "recommendation": self.recommendation
        }

class RiskEngine:
    """Combines forensic findings, OCR confidence, metadata flags, and ML predictions."""

    @classmethod
    def evaluate(
        cls,
        forensic_findings: List[ForensicFinding],
        ocr_confidence_avg: float,
        extracted_fields: Dict[str, Any],
        ml_prediction: Optional[Dict[str, Any]] = None,
        issuer_configured: bool = False
    ) -> RiskAssessment:
        evidence = []
        score = 0.0

        # Category mapping function
        def get_fraud_category(signal_name: str) -> str:
            name = signal_name.lower()
            if any(k in name for k in ["genai", "spectral", "diffusion", "synthetic"]):
                return "SYNTHETIC_GENAI"
            elif any(k in name for k in ["mrz", "producer", "editor", "stripped", "counterfeit"]):
                return "COUNTERFEITING"
            elif any(k in name for k in ["ela", "copy_move", "math", "chronological", "alignment", "inconsistency", "noise"]):
                return "ALTERATION"
            return "GENERAL_INTEGRITY"

        # 1. Forensic signals evaluation with calibrated signal weighting
        for finding in forensic_findings:
            category = get_fraud_category(finding.feature_name)
            name = finding.feature_name.lower()

            # Deterministic, high-certainty forgery indicators
            is_definitive = any(k in name for k in [
                "meta_suspicious_producer", "metadata_anomaly", "mrz", "math", "copy_move", "genai"
            ])

            if finding.severity == "HIGH":
                pts = 35.0 if is_definitive else 18.0
                score += pts
                evidence.append({
                    "signal": finding.feature_name,
                    "category": category,
                    "severity": "HIGH",
                    "impact": f"+{pts:.0f} pts",
                    "finding": finding.explanation
                })
            elif finding.severity == "MEDIUM":
                pts = 14.0 if is_definitive else 8.0
                score += pts
                evidence.append({
                    "signal": finding.feature_name,
                    "category": category,
                    "severity": "MEDIUM",
                    "impact": f"+{pts:.0f} pts",
                    "finding": finding.explanation
                })

        # 2. OCR text extraction confidence (informational with low penalty for degradation)
        if ocr_confidence_avg < 0.60:
            score += 8.0
            evidence.append({
                "signal": "ocr_confidence",
                "category": "GENERAL_INTEGRITY",
                "severity": "MEDIUM",
                "impact": "+8 pts",
                "finding": f"Low overall OCR confidence ({ocr_confidence_avg*100:.1f}%). Document scan quality may be low-resolution or noisy."
            })
        else:
            evidence.append({
                "signal": "ocr_confidence",
                "category": "GENERAL_INTEGRITY",
                "severity": "INFO",
                "impact": "0 pts",
                "finding": f"Document text exhibits strong optical clarity with {ocr_confidence_avg*100:.1f}% average character confidence."
            })

        # 3. Field presence assessment (Informational - never penalize as fraud)
        critical_fields = ["student_name", "institution_name", "degree_course"]
        missing_critical = [f for f in critical_fields if not extracted_fields.get(f, {}).get("value")]
        if missing_critical:
            evidence.append({
                "signal": "field_presence_analysis",
                "category": "GENERAL_INTEGRITY",
                "severity": "INFO",
                "impact": "0 pts",
                "finding": f"Entities not detected or labeled under standard academic keywords: {', '.join(missing_critical)}. (Zero fraud penalty: document may be a non-academic credential, ID, or custom template)."
            })
        else:
            evidence.append({
                "signal": "field_presence_analysis",
                "category": "GENERAL_INTEGRITY",
                "severity": "INFO",
                "impact": "0 pts",
                "finding": "All primary credential entities successfully extracted and indexed."
            })

        # 4. ML Model prediction incorporation (if available)
        if ml_prediction and ml_prediction.get("is_available") and ml_prediction.get("fraud_probability") is not None:
            fraud_prob = ml_prediction["fraud_probability"]
            # Weight ML model cleanly alongside deterministic forensics
            ml_contribution = fraud_prob * 25.0
            score = (score * 0.75) + ml_contribution
            if fraud_prob >= 0.50:
                severity = "HIGH" if fraud_prob >= 0.75 else "MEDIUM"
                evidence.append({
                    "signal": "ml_supervised_classifier",
                    "category": "GENERAL_INTEGRITY",
                    "severity": severity,
                    "impact": f"+{ml_contribution:.1f} pts",
                    "finding": f"Trained classifier predicted alteration likelihood at {fraud_prob*100:.1f}%."
                })
        else:
            evidence.append({
                "signal": "ml_supervised_classifier",
                "category": "GENERAL_INTEGRITY",
                "severity": "INFO",
                "impact": "0 pts",
                "finding": "Supervised ML model artifact inactive or unavailable. Risk assessment calibrated on deterministic multi-pillar forensics."
            })

        # Clamp score to [0.0, 100.0]
        final_score = min(100.0, max(0.0, score))

        # Calibrate risk tier
        if final_score < 25.0:
            risk_level = "LOW_RISK"
            recommendation = "Document exhibits uniform forensic integrity with clean structural properties. No suspicious alteration or counterfeiting traces detected."
        elif final_score < 55.0:
            risk_level = "MEDIUM_RISK"
            recommendation = "Document displays minor anomalies, compression variance, or degraded OCR legibility. Secondary human review advised to inspect highlighted regions."
        else:
            risk_level = "HIGH_RISK"
            recommendation = "Multiple high-severity anomalies detected (e.g. metadata software signatures, copy-move clusters, or MRZ/math mismatches). Direct credential issuer verification recommended."

        # Truthful issuer status
        issuer_status = "Issuer verification unavailable (Not configured)"
        if issuer_configured:
            issuer_status = "Configured (Awaiting institutional API handshake)"

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=final_score,
            summary_evidence=evidence,
            issuer_verification_status=issuer_status,
            recommendation=recommendation
        )
