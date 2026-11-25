"""End-to-end document verification pipeline service."""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.storage import get_storage
from backend.app.models.entities import (
    Document, VerificationJob, OCRResult, DocumentField,
    ForensicResult, ModelPrediction, VerificationResult, Report, AuditLog
)
from ai.preprocessing.pdf_converter import DocumentPreprocessor
from ai.ocr.engine import StandardOCREngine
from ai.field_extraction.academic_extractor import AcademicFieldExtractor
from ai.forensics.analyzer import DocumentForensicsAnalyzer
from ai.features.schema import build_feature_dict
from ai.inference.service import MLInferenceService
from ai.risk_engine.engine import RiskEngine
from reports.generator import VerificationReportGenerator

logger = logging.getLogger(__name__)

class VerificationService:
    """Orchestrates end-to-end document forensic screening and reporting."""

    @classmethod
    def execute_verification(cls, document_id: str, db: Session) -> Dict[str, Any]:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        # Find or create job
        job = db.query(VerificationJob).filter(VerificationJob.document_id == document_id).order_by(VerificationJob.created_at.desc()).first()
        if not job or job.status == "COMPLETED":
            job = VerificationJob(
                document_id=document_id,
                status="PROCESSING",
                current_stage="INITIALIZING",
                progress_percent=5,
                started_at=datetime.utcnow()
            )
            db.add(job)
        else:
            job.status = "PROCESSING"
            job.current_stage = "INITIALIZING"
            job.progress_percent = 5
            job.started_at = datetime.utcnow()
            job.error_message = None

        doc.status = "PROCESSING"
        db.commit()

        storage = get_storage()
        try:
            # 1. Retrieve physical file
            local_file_path = storage.get_path(doc.storage_key)

            # 2. PDF & Page Rendering
            job.current_stage = "DOCUMENT_PREPROCESSING"
            job.progress_percent = 15
            db.commit()

            page_images = DocumentPreprocessor.load_document_images(local_file_path, doc.mime_type)
            doc.page_count = len(page_images)
            
            pdf_metadata = {}
            if doc.mime_type == "application/pdf":
                pdf_metadata = DocumentPreprocessor.extract_pdf_metadata(local_file_path)
                doc.metadata_info = pdf_metadata

            # 3. OCR Processing
            job.current_stage = "OCR_EXTRACTION"
            job.progress_percent = 35
            db.commit()

            ocr_engine = StandardOCREngine()
            ocr_page_results = ocr_engine.process_document(local_file_path, doc.mime_type, page_images)

            # Persist OCR results
            # Clear any previous results if re-analyzing
            db.query(OCRResult).filter(OCRResult.document_id == document_id).delete()
            for ocr_res in ocr_page_results:
                db_ocr = OCRResult(
                    document_id=document_id,
                    page_number=ocr_res.page_number,
                    extracted_text=ocr_res.text,
                    confidence_avg=ocr_res.confidence_avg,
                    word_count=ocr_res.word_count,
                    bounding_boxes=ocr_res.bounding_boxes
                )
                db.add(db_ocr)

            # 4. Academic Field Extraction
            job.current_stage = "FIELD_EXTRACTION"
            job.progress_percent = 50
            db.commit()

            extracted_fields = AcademicFieldExtractor.extract_fields(ocr_page_results)
            db.query(DocumentField).filter(DocumentField.document_id == document_id).delete()
            for field_name, field_data in extracted_fields.items():
                db_field = DocumentField(
                    document_id=document_id,
                    field_name=field_name,
                    field_value=field_data["value"],
                    confidence=field_data["confidence"],
                    bounding_box=field_data["bounding_box"]
                )
                db.add(db_field)

            # 5. Computer Vision & Forensics
            job.current_stage = "FORENSIC_ANALYSIS"
            job.progress_percent = 65
            db.commit()

            all_bboxes = []
            for pr in ocr_page_results:
                all_bboxes.extend(pr.bounding_boxes)

            # Save ELA artifact
            ela_rel_dir = os.path.join("artifacts", document_id)
            ela_abs_dir = os.path.join(settings.STORAGE_LOCAL_PATH, ela_rel_dir)
            os.makedirs(ela_abs_dir, exist_ok=True)
            ela_file_path = os.path.join(ela_abs_dir, "ela_analysis.jpg")

            primary_page_img = page_images[0] if page_images else None
            findings, forensic_features = DocumentForensicsAnalyzer.analyze_page(
                image=primary_page_img,
                page_num=1,
                pdf_metadata=pdf_metadata,
                ocr_bboxes=all_bboxes,
                save_ela_path=ela_file_path
            )

            db.query(ForensicResult).filter(ForensicResult.document_id == document_id).delete()
            for f in findings:
                db_forensic = ForensicResult(
                    document_id=document_id,
                    feature_name=f.feature_name,
                    measured_value=f.measured_value,
                    threshold=f.threshold,
                    severity=f.severity,
                    explanation=f.explanation,
                    localized_regions=f.localized_regions
                )
                db.add(db_forensic)

            # 6. ML Inference
            job.current_stage = "ML_PREDICTION"
            job.progress_percent = 78
            db.commit()

            feature_dict = build_feature_dict(
                ocr_results=ocr_page_results,
                forensic_features=forensic_features,
                extracted_fields=extracted_fields,
                mime_type=doc.mime_type,
                page_count=doc.page_count
            )
            ml_prediction = MLInferenceService.predict(feature_dict)

            db.query(ModelPrediction).filter(ModelPrediction.document_id == document_id).delete()
            db_ml = ModelPrediction(
                document_id=document_id,
                model_name=ml_prediction["model_name"],
                model_version=ml_prediction["model_version"],
                fraud_probability=ml_prediction["fraud_probability"] or 0.0,
                prediction_label=ml_prediction["prediction_label"],
                feature_vector=feature_dict
            )
            db.add(db_ml)

            # 7. Risk Engine Scoring
            job.current_stage = "RISK_AGGREGATION"
            job.progress_percent = 88
            db.commit()

            ocr_conf = float(ocr_page_results[0].confidence_avg) if ocr_page_results else 0.0
            assessment = RiskEngine.evaluate(
                forensic_findings=findings,
                ocr_confidence_avg=ocr_conf,
                extracted_fields=extracted_fields,
                ml_prediction=ml_prediction,
                issuer_configured=settings.DIGILOCKER_ENABLED
            )

            import uuid as _uuid
            verif_id = str(_uuid.uuid4())

            db.query(Report).filter(Report.document_id == document_id).delete()
            db.query(VerificationResult).filter(VerificationResult.document_id == document_id).delete()
            db_verif = VerificationResult(
                id=verif_id,
                document_id=document_id,
                risk_level=assessment.risk_level,
                risk_score=assessment.risk_score,
                summary_evidence=assessment.summary_evidence,
                issuer_verification_status=assessment.issuer_verification_status,
                recommendation=assessment.recommendation
            )
            db.add(db_verif)

            # 8. Report Generation
            job.current_stage = "REPORT_GENERATION"
            job.progress_percent = 95

            reports_rel_path = f"reports/docshield_report_{document_id}.pdf"
            reports_abs_path = os.path.join(settings.STORAGE_LOCAL_PATH, reports_rel_path)

            doc_info = {
                "id": doc.id,
                "filename": doc.original_filename,
                "file_hash": doc.file_hash_sha256,
                "mime_type": doc.mime_type,
                "file_size_bytes": doc.file_size_bytes
            }
            fields_list = [
                {"field_name": k, "field_value": v["value"], "confidence": v["confidence"]}
                for k, v in extracted_fields.items()
            ]
            forensic_dicts = [f.to_dict() for f in findings]

            VerificationReportGenerator.generate(
                output_path=reports_abs_path,
                document_info=doc_info,
                verification_result=assessment.to_dict(),
                extracted_fields=fields_list,
                forensic_findings=forensic_dicts,
                ml_prediction=ml_prediction
            )

            report_size = os.path.getsize(reports_abs_path) if os.path.exists(reports_abs_path) else 0
            db_report = Report(
                document_id=document_id,
                verification_result_id=verif_id,
                report_storage_key=reports_rel_path,
                file_size_bytes=report_size,
                download_count=0
            )
            db.add(db_report)

            # 9. Complete Job
            job.status = "COMPLETED"
            job.current_stage = "VERIFICATION_COMPLETE"
            job.progress_percent = 100
            job.completed_at = datetime.utcnow()
            doc.status = "COMPLETED"

            # Create Audit Log
            audit = AuditLog(
                user_id=doc.user_id,
                action="DOCUMENT_ANALYSIS_COMPLETED",
                resource_type="document",
                resource_id=doc.id,
                details={
                    "risk_level": assessment.risk_level,
                    "risk_score": assessment.risk_score,
                    "report_id": db_report.id
                }
            )
            db.add(audit)
            db.commit()

            logger.info(f"Document {document_id} successfully verified. Risk: {assessment.risk_level} ({assessment.risk_score})")
            return {
                "status": "COMPLETED",
                "verification_id": db_verif.id,
                "risk_level": assessment.risk_level,
                "risk_score": assessment.risk_score
            }

        except Exception as e:
            logger.error(f"Verification pipeline failed for document {document_id}: {e}", exc_info=True)
            db.rollback()
            job.status = "FAILED"
            job.current_stage = "FAILED"
            job.error_message = f"Analysis pipeline failed: {str(e)}"
            doc.status = "FAILED"
            db.commit()
            raise
