"""PDF verification report generation using ReportLab."""
import os
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class VerificationReportGenerator:
    """Generates comprehensive, multi-page PDF verification reports."""

    @classmethod
    def generate(
        cls,
        output_path: str,
        document_info: Dict[str, Any],
        verification_result: Dict[str, Any],
        extracted_fields: List[Dict[str, Any]],
        forensic_findings: List[Dict[str, Any]],
        ml_prediction: Optional[Dict[str, Any]] = None
    ) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocShieldTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "DocShieldSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748B")
        )
        section_style = ParagraphStyle(
            "DocShieldSection",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1E293B"),
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "DocShieldBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        legal_style = ParagraphStyle(
            "DocShieldLegal",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748B")
        )

        elements = []

        # Header
        elements.append(Paragraph("DocShield AI", title_style))
        elements.append(Paragraph("AI-Based Document Fraud Detection and Verification System", subtitle_style))
        elements.append(Paragraph(f"Official Integrity Assessment Report — Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284C7"), spaceAfter=14))

        # Risk Assessment Summary Card
        risk_level = verification_result.get("risk_level", "INCONCLUSIVE")
        risk_score = verification_result.get("risk_score", 0.0)

        if risk_level == "LOW_RISK":
            badge_color = colors.HexColor("#15803D")
            badge_bg = colors.HexColor("#DCFCE7")
            badge_text = "LOW RISK / INTEGRITY VERIFIED"
        elif risk_level == "MEDIUM_RISK":
            badge_color = colors.HexColor("#B45309")
            badge_bg = colors.HexColor("#FEF3C7")
            badge_text = "MEDIUM RISK / SUSPICIOUS ANOMALIES"
        else:
            badge_color = colors.HexColor("#B91C1C")
            badge_bg = colors.HexColor("#FEE2E2")
            badge_text = "HIGH RISK / ELEVATED TAMPERING PROBABILITY"

        summary_data = [
            [
                Paragraph("<b>ASSESSMENT VERDICT</b>", body_style),
                Paragraph(f"<b><font color='{badge_color.hexval()}'>{badge_text}</font></b>", body_style),
                Paragraph("<b>CALIBRATED RISK SCORE</b>", body_style),
                Paragraph(f"<b>{risk_score:.1f} / 100</b>", body_style)
            ],
            [
                Paragraph("<b>DOCUMENT ID</b>", body_style),
                Paragraph(document_info.get("id", "N/A"), body_style),
                Paragraph("<b>ORIGINAL FILE</b>", body_style),
                Paragraph(document_info.get("filename", "N/A"), body_style)
            ],
            [
                Paragraph("<b>SHA-256 DIGEST</b>", body_style),
                Paragraph(f"<font size=7>{document_info.get('file_hash', 'N/A')}</font>", body_style),
                Paragraph("<b>FILE FORMAT / SIZE</b>", body_style),
                Paragraph(f"{document_info.get('mime_type', 'N/A')} ({document_info.get('file_size_bytes', 0) // 1024} KB)", body_style)
            ]
        ]

        t_summary = Table(summary_data, colWidths=[1.4*inch, 2.2*inch, 1.4*inch, 2.0*inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 14))

        # Academic Fields Section
        elements.append(Paragraph("1. Extracted Academic Certificate Information", section_style))
        fields_table_data = [
            [Paragraph("<b>Entity Field</b>", body_style), Paragraph("<b>Extracted Value</b>", body_style), Paragraph("<b>Confidence</b>", body_style), Paragraph("<b>Status</b>", body_style)]
        ]
        
        field_labels = {
            "student_name": "Student Full Name",
            "institution_name": "University / Institution",
            "degree_course": "Degree / Course Title",
            "roll_number": "Roll / Registration Number",
            "certificate_number": "Certificate Number",
            "issue_date": "Issue Date",
            "marks_grade": "Marks / CGPA / Grade"
        }

        for f in extracted_fields:
            fname = field_labels.get(f.get("field_name"), f.get("field_name"))
            fval = f.get("field_value") or "Not Detected"
            conf = f.get("confidence", 0.0)
            status_text = "Detected" if f.get("field_value") else "Missing"
            fields_table_data.append([
                Paragraph(fname, body_style),
                Paragraph(fval, body_style),
                Paragraph(f"{conf*100:.1f}%" if f.get("field_value") else "N/A", body_style),
                Paragraph(status_text, body_style)
            ])

        t_fields = Table(fields_table_data, colWidths=[2.0*inch, 3.2*inch, 0.9*inch, 0.9*inch])
        t_fields.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(t_fields)
        elements.append(Spacer(1, 14))

        # Forensic Findings Section
        elements.append(Paragraph("2. Computer Vision & Document Forensics Findings", section_style))
        forensic_table_data = [
            [Paragraph("<b>Forensic Method</b>", body_style), Paragraph("<b>Value / Threshold</b>", body_style), Paragraph("<b>Severity</b>", body_style), Paragraph("<b>Finding & Rationale</b>", body_style)]
        ]

        for finding in forensic_findings:
            sev = finding.get("severity", "LOW")
            sev_color = "#15803D" if sev == "LOW" else ("#B45309" if sev == "MEDIUM" else "#B91C1C")
            forensic_table_data.append([
                Paragraph(finding.get("feature_name", "").replace("_", " ").title(), body_style),
                Paragraph(f"{finding.get('measured_value', 0):.2f} / {finding.get('threshold', 0):.2f}", body_style),
                Paragraph(f"<b><font color='{sev_color}'>{sev}</font></b>", body_style),
                Paragraph(finding.get("explanation", ""), body_style)
            ])

        t_forensics = Table(forensic_table_data, colWidths=[1.8*inch, 1.2*inch, 0.8*inch, 3.2*inch])
        t_forensics.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(t_forensics)
        elements.append(Spacer(1, 14))

        # ML and Issuer Verification Section
        elements.append(Paragraph("3. Machine Learning & External Issuer Assessment", section_style))
        ml_data = []
        if ml_prediction and ml_prediction.get("is_available"):
            ml_data.append([
                Paragraph("<b>ML Model Architecture</b>", body_style),
                Paragraph(f"{ml_prediction.get('model_name', 'Random Forest')} (v{ml_prediction.get('model_version', '1.0')})", body_style)
            ])
            ml_data.append([
                Paragraph("<b>Fraud Probability</b>", body_style),
                Paragraph(f"{ml_prediction.get('fraud_probability', 0.0)*100:.1f}% ({ml_prediction.get('prediction_label', 'AUTHENTIC')})", body_style)
            ])
        else:
            ml_data.append([
                Paragraph("<b>ML Model Status</b>", body_style),
                Paragraph("Model not trained / unavailable. Heuristic rule & forensic analysis active.", body_style)
            ])
        
        ml_data.append([
            Paragraph("<b>External Issuer Check</b>", body_style),
            Paragraph(verification_result.get("issuer_verification_status", "Issuer verification unavailable (Not configured)"), body_style)
        ])
        ml_data.append([
            Paragraph("<b>Final Recommendation</b>", body_style),
            Paragraph(verification_result.get("recommendation", "Review required."), body_style)
        ])

        t_ml = Table(ml_data, colWidths=[2.2*inch, 4.8*inch])
        t_ml.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_ml)
        elements.append(Spacer(1, 16))

        # Legal Disclaimer
        elements.append(Paragraph("<b>Notice & Legal Limitations:</b>", legal_style))
        elements.append(Paragraph(
            "This report provides an automated document-integrity assessment. It is not, by itself, legal proof of authenticity "
            "or fraud. Suspicious or inconclusive cases should be reviewed by an authorized human or credential issuer. "
            "Generated by DocShield AI under Project Guidelines 2026-27.",
            legal_style
        ))

        doc.build(elements)
        return output_path
