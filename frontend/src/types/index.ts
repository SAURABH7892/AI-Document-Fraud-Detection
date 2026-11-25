export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  file_hash_sha256: string;
  document_type: string;
  status: 'UPLOADED' | 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  page_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentField {
  field_name: string;
  field_value: string | null;
  confidence: number;
  bounding_box: number[] | null;
}

export interface ForensicFinding {
  feature_name: string;
  measured_value: number;
  threshold: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  explanation: string;
  localized_regions: any[];
}

export interface ModelPrediction {
  model_name: string;
  model_version: string;
  fraud_probability: number | null;
  prediction_label: string;
  feature_vector?: Record<string, number>;
}

export interface VerificationDetail {
  id: string;
  document_id: string;
  risk_level: 'LOW_RISK' | 'MEDIUM_RISK' | 'HIGH_RISK' | 'INCONCLUSIVE';
  risk_score: number;
  summary_evidence: Array<{
    signal: string;
    category?: string;
    severity: string;
    impact: string;
    finding: string;
  }>;
  issuer_verification_status: string;
  recommendation: string;
  created_at: string;
  document: DocumentItem;
  fields: DocumentField[];
  forensics: ForensicFinding[];
  ml_prediction: ModelPrediction | null;
  report_id: string | null;
}

export interface DashboardStats {
  total_documents: number;
  completed_verifications: number;
  pending_jobs: number;
  failed_jobs: number;
  risk_distribution: {
    LOW_RISK: number;
    MEDIUM_RISK: number;
    HIGH_RISK: number;
    INCONCLUSIVE: number;
  };
  recent_documents: DocumentItem[];
}
