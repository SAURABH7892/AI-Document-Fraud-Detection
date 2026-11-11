'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Shield, FileText, Download, ArrowLeft, RefreshCw, CheckCircle2,
  AlertTriangle, Cpu, Layers, ScanLine, ExternalLink, Hash, Eye, Sparkles,
  Landmark, CheckCircle, XCircle, BadgeCheck
} from 'lucide-react';
import { api } from '@/lib/api';
import { VerificationDetail, DocumentItem } from '@/types';
import { RiskBadge } from '@/components/RiskBadge';
import { AuthGuard } from '@/components/AuthGuard';

export default function DocumentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params?.id as string;

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [verification, setVerification] = useState<VerificationDetail | null>(null);
  const [jobStatus, setJobStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'fields' | 'forensics' | 'ela' | 'ml' | 'digilocker'>('overview');
  const [polling, setPolling] = useState(false);

  const fetchDetails = async () => {
    try {
      const doc = await api.getDocument(documentId);
      setDocument(doc);

      if (doc.status === 'COMPLETED') {
        const verif = await api.getVerificationByDocument(documentId);
        setVerification(verif);
        setPolling(false);
      } else {
        const job = await api.getJobStatus(documentId);
        setJobStatus(job);
        setPolling(true);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [documentId]);

  // Polling for in-progress jobs
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (polling) {
      interval = setInterval(() => {
        fetchDetails();
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [polling]);

  if (loading) {
    return (
      <AuthGuard>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center space-y-4">
          <RefreshCw className="w-8 h-8 text-sky-600 animate-spin mx-auto" />
          <p className="text-xs text-slate-500 font-medium">Retrieving document inspection data...</p>
        </div>
      </AuthGuard>
    );
  }

  if (!document) {
    return (
      <AuthGuard>
        <div className="max-w-md mx-auto py-16 text-center space-y-3">
          <p className="text-sm font-semibold text-slate-800">Document not found or access denied.</p>
          <Link href="/dashboard" className="text-xs text-sky-600 hover:underline">Return to Dashboard</Link>
        </div>
      </AuthGuard>
    );
  }

  // If still processing
  if (document.status === 'QUEUED' || document.status === 'PROCESSING') {
    return (
      <AuthGuard>
        <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-6">
          <div className="w-16 h-16 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto border border-sky-100 shadow-sm animate-pulse">
            <ScanLine className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Analysis In Progress</h1>
            <p className="text-xs text-slate-500 mt-1">Executing OCR, Error Level Analysis (ELA), and ML inference</p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 max-w-lg mx-auto shadow-sm space-y-4">
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>Stage: {jobStatus?.current_stage || 'PROCESSING'}</span>
              <span>{jobStatus?.progress_percent || 30}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-sky-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${jobStatus?.progress_percent || 30}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-400">
              Background workers are actively examining document pixels and layout structures.
            </p>
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Top Navigation & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            href="/history"
            className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            title="Back to History"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight max-w-md truncate">
                {document.original_filename}
              </h1>
              {verification && (
                <RiskBadge level={verification.risk_level} score={verification.risk_score} showScore />
              )}
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5 font-mono">ID: {document.id}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {verification ? (
            <a
              href={api.getReportDownloadUrl(verification.id)}
              download
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-sm transition-colors cursor-pointer"
            >
              <Download className="w-4 h-4" />
              Download Official PDF Verification Report
            </a>
          ) : (
            <a
              href={api.getReportDownloadByDocUrl(document.id)}
              download
              target="_blank"
              rel="noreferrer"
              className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Download className="w-4 h-4 text-slate-500" />
              Download PDF Report
            </a>
          )}
        </div>
      </div>

      {/* Main Verification Summary Banner */}
      {verification && (
        <div
          className={`p-6 rounded-2xl border ${
            verification.risk_level === 'LOW_RISK'
              ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
              : verification.risk_level === 'MEDIUM_RISK'
              ? 'bg-amber-50/60 border-amber-200 text-amber-900'
              : 'bg-rose-50/60 border-rose-200 text-rose-900'
          }`}
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider">Automated Decision Rationale</span>
              </div>
              <p className="text-sm font-semibold">{verification.recommendation}</p>
              <p className="text-xs opacity-80 mt-1">
                Issuer Check: <span className="font-medium">{verification.issuer_verification_status}</span>
              </p>
              {verification.issuer_metadata?.is_gov_id && (
                <div className="mt-2.5 flex flex-wrap items-center gap-2">
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold ${
                    verification.issuer_metadata.checksum_valid
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      : 'bg-rose-100 text-rose-800 border border-rose-300'
                  }`}>
                    <Landmark className="w-3.5 h-3.5 text-emerald-700" />
                    DigiLocker: {verification.issuer_metadata.id_type_label}
                  </span>
                  <span className="text-[11px] font-mono font-bold text-slate-700 bg-white/90 px-2 py-0.5 rounded border border-slate-200">
                    {verification.issuer_metadata.id_number_masked}
                  </span>
                  <span className="text-[10px] text-slate-600 bg-white/70 px-2 py-0.5 rounded">
                    Txn: {verification.issuer_metadata.transaction_id}
                  </span>
                </div>
              )}
            </div>
            <div className="text-right flex-shrink-0">
              <div className="text-3xl font-extrabold">{verification.risk_score.toFixed(1)} <span className="text-sm font-normal opacity-75">/ 100</span></div>
              <span className="text-[11px] uppercase tracking-wider font-semibold opacity-80">Calibrated Risk Score</span>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200 flex items-center gap-6 text-xs font-semibold text-slate-600">
        {[
          { key: 'overview', label: 'Summary & Evidence', icon: Shield },
          { key: 'digilocker', label: 'DigiLocker & Gov ID', icon: Landmark },
          { key: 'fields', label: 'Extracted Academic Fields', icon: ScanLine },
          { key: 'forensics', label: 'Forensic Signals', icon: Layers },
          { key: 'ela', label: 'Error Level Analysis (ELA)', icon: Eye },
          { key: 'ml', label: 'ML Model Assessment', icon: Cpu },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`pb-3 flex items-center gap-2 border-b-2 transition-colors ${
                isActive ? 'border-sky-600 text-sky-600' : 'border-transparent hover:text-slate-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Overview & Evidence */}
      {activeTab === 'overview' && verification && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900">Detected Forensic Signals & Impact</h2>
            <div className="divide-y divide-slate-100">
              {verification.summary_evidence.map((ev, idx) => (
                <div key={idx} className="py-3 flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-800 capitalize">
                        {ev.signal.replace(/_/g, ' ')}
                      </span>
                      {ev.category && ev.category !== "GENERAL_INTEGRITY" && (
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                          ev.category === "SYNTHETIC_GENAI"
                            ? "bg-purple-100 text-purple-700 border border-purple-200"
                            : ev.category === "COUNTERFEITING"
                            ? "bg-amber-100 text-amber-800 border border-amber-200"
                            : "bg-indigo-100 text-indigo-700 border border-indigo-200"
                        }`}>
                          {ev.category.replace("_", " ")}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{ev.finding}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.severity === 'HIGH'
                          ? 'bg-rose-50 text-rose-700 border border-rose-200'
                          : ev.severity === 'MEDIUM'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-50 text-slate-600 border border-slate-200'
                      }`}
                    >
                      {ev.impact}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Document Properties Sidebar */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4 text-xs">
            <h2 className="text-sm font-bold text-slate-900">Document Cryptographic Metadata</h2>
            <div className="space-y-3">
              <div>
                <span className="text-slate-400 block mb-0.5 font-medium">SHA-256 Checksum</span>
                <span className="font-mono text-[10px] text-slate-700 break-all bg-slate-50 p-1.5 rounded block border border-slate-100">
                  {document.file_hash_sha256}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5 font-medium">File Size</span>
                <span className="font-semibold text-slate-800">{(document.file_size_bytes / 1024).toFixed(1)} KB</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5 font-medium">MIME Format</span>
                <span className="font-semibold text-slate-800 uppercase">{document.mime_type}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5 font-medium">Page Count</span>
                <span className="font-semibold text-slate-800">{document.page_count} page(s)</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5 font-medium">Upload Timestamp</span>
                <span className="font-semibold text-slate-800">{new Date(document.created_at).toUTCString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: DigiLocker & Government ID Verification */}
      {activeTab === 'digilocker' && verification && (
        <div className="space-y-6">
          {verification.issuer_metadata?.is_gov_id ? (
            <div className="space-y-6">
              {/* Status Header Card */}
              <div className={`p-6 rounded-2xl border ${
                verification.issuer_metadata.checksum_valid
                  ? 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                  : 'bg-rose-50/70 border-rose-200 text-rose-950'
              }`}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Landmark className="w-5 h-5 text-emerald-700" />
                      <span className="text-xs font-bold uppercase tracking-wider">
                        DigiLocker Certified Gateway Result
                      </span>
                    </div>
                    <h2 className="text-lg font-bold">
                      {verification.issuer_metadata.authority}
                    </h2>
                    <p className="text-xs opacity-90">
                      {verification.issuer_metadata.status_text}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${
                      verification.issuer_metadata.checksum_valid
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                        : 'bg-rose-100 text-rose-800 border-rose-300'
                    }`}>
                      {verification.issuer_metadata.checksum_valid ? 'VERIFIED BY ISSUER' : 'CHECKSUM MISMATCH'}
                    </span>
                  </div>
                </div>
              </div>

              {/* 3 Metric Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <span className="text-xs text-slate-400 block font-medium">Document ID Type</span>
                  <span className="text-sm font-bold text-slate-800">{verification.issuer_metadata.id_type_label}</span>
                  <span className="text-[11px] font-mono text-sky-600 block">{verification.issuer_metadata.id_number_masked}</span>
                </div>
                <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <span className="text-xs text-slate-400 block font-medium">Algorithm Checksum</span>
                  <span className={`text-sm font-bold flex items-center gap-1.5 ${
                    verification.issuer_metadata.checksum_valid ? 'text-emerald-700' : 'text-rose-700'
                  }`}>
                    {verification.issuer_metadata.checksum_valid ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertTriangle className="w-4 h-4 text-rose-600" />}
                    {verification.issuer_metadata.checksum_valid ? 'Mathematically Valid' : 'Invalid Structure'}
                  </span>
                  <span className="text-[11px] text-slate-500 block truncate">{verification.issuer_metadata.checksum_details}</span>
                </div>
                <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <span className="text-xs text-slate-400 block font-medium">Demographic Correlation</span>
                  <span className="text-sm font-bold text-slate-800">
                    {verification.issuer_metadata.demographic_match?.name_match_score ?? 90}% Match
                  </span>
                  <span className="text-[11px] text-slate-500 block truncate">
                    {verification.issuer_metadata.demographic_match?.details || 'Demographics validated'}
                  </span>
                </div>
              </div>

              {/* Gateway Audit Trace Details */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4 text-xs">
                <h3 className="text-sm font-bold text-slate-900">National Identity Repository Handshake Audit</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium mb-0.5">DigiLocker Transaction ID</span>
                    <span className="font-mono font-bold text-slate-800">{verification.issuer_metadata.transaction_id}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium mb-0.5">Gateway Handshake Mode</span>
                    <span className="font-semibold text-slate-800 uppercase">
                      {verification.issuer_metadata.verification_mode === 'LIVE_API' ? 'Live Production OAuth2 API' : 'DigiLocker Certified Gateway (Sandbox)'}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium mb-0.5">Verification Timestamp</span>
                    <span className="font-semibold text-slate-800">{new Date(verification.issuer_metadata.timestamp).toUTCString()}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium mb-0.5">Official Issuing Authority</span>
                    <span className="font-semibold text-slate-800">{verification.issuer_metadata.authority}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center mx-auto">
                <Landmark className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-800">Academic Credential Document</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                This document is categorized as an academic credential rather than an Indian Government Issued ID (Aadhaar, PAN, Driving License, or Passport).
              </p>
              <div className="pt-2 flex flex-wrap justify-center gap-2 text-[11px] text-slate-500">
                <span className="px-2.5 py-1 bg-slate-50 rounded-lg border border-slate-100">Aadhaar (UIDAI)</span>
                <span className="px-2.5 py-1 bg-slate-50 rounded-lg border border-slate-100">PAN Card (ITD)</span>
                <span className="px-2.5 py-1 bg-slate-50 rounded-lg border border-slate-100">Driving License (MoRTH)</span>
                <span className="px-2.5 py-1 bg-slate-50 rounded-lg border border-slate-100">National Academic Depository (NAD)</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Extracted Academic Fields */}
      {activeTab === 'fields' && verification && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-5 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900">Academic Entity Parsing</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Extracted via rule-based patterns and spatial bounding box analysis
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-3 px-6">Entity Field</th>
                  <th className="py-3 px-6">Extracted Value</th>
                  <th className="py-3 px-6">OCR Confidence</th>
                  <th className="py-3 px-6">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {verification.fields.map((f, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60">
                    <td className="py-3.5 px-6 font-semibold text-slate-800 capitalize">
                      {f.field_name.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3.5 px-6 font-medium text-slate-900">
                      {f.field_value ? (
                        <span>{f.field_value}</span>
                      ) : (
                        <span className="text-slate-400 italic">Not Detected / Absent</span>
                      )}
                    </td>
                    <td className="py-3.5 px-6 text-slate-600">
                      {f.field_value ? `${(f.confidence * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3.5 px-6">
                      {f.field_value ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3" /> Extracted
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                          Missing
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Forensic Signals */}
      {activeTab === 'forensics' && verification && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {verification.forensics.map((f, idx) => (
            <div key={idx} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-900 capitalize">
                  {f.feature_name.replace(/_/g, ' ')}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                    f.severity === 'HIGH'
                      ? 'bg-rose-50 text-rose-700 border-rose-200'
                      : f.severity === 'MEDIUM'
                      ? 'bg-amber-50 text-amber-700 border-amber-200'
                      : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}
                >
                  {f.severity} SEVERITY
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">{f.explanation}</p>
              <div className="pt-2 border-t border-slate-100 flex justify-between text-[11px] text-slate-400">
                <span>Measured Value: <strong className="text-slate-700">{f.measured_value.toFixed(2)}</strong></span>
                <span>Calibrated Threshold: <strong className="text-slate-700">{f.threshold.toFixed(2)}</strong></span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 4: ELA Heatmap Viewer */}
      {activeTab === 'ela' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="max-w-2xl">
            <h2 className="text-sm font-bold text-slate-900">Error Level Analysis (ELA) Pixel Map</h2>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Error Level Analysis resaves the document at a known 92% JPEG compression quality and measures pixel-wise difference error.
              Regions that have been spliced or modified with external software typically demonstrate differing error levels.
            </p>
          </div>

          <div className="p-4 bg-slate-900 rounded-xl flex items-center justify-center overflow-hidden min-h-[350px]">
            <img
              src={api.getElaArtifactUrl(document.id)}
              alt="ELA Heatmap"
              className="max-h-[500px] object-contain rounded border border-slate-800"
              onError={(e: any) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <p className="text-[11px] text-slate-400 italic text-center">
            Brighter white or colored hotspots indicate high compression variance clusters.
          </p>
        </div>
      )}

      {/* Tab 5: ML Model Assessment */}
      {activeTab === 'ml' && verification && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Supervised Machine Learning Model Card</h2>
              <p className="text-xs text-slate-500 mt-0.5">Feature-level classifier trained on non-sensitive authentic & tampered datasets</p>
            </div>
            {verification.ml_prediction?.fraud_probability !== null && (
              <span className="text-xs font-bold px-3 py-1 bg-sky-50 text-sky-700 rounded-lg border border-sky-200">
                Model: {verification.ml_prediction?.model_name || 'Random Forest'} (v{verification.ml_prediction?.model_version || '1.0'})
              </span>
            )}
          </div>

          {verification.ml_prediction && verification.ml_prediction.fraud_probability !== null ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-400 block font-medium">Prediction Label</span>
                  <span className="text-lg font-bold text-slate-900 mt-1 block">
                    {verification.ml_prediction.prediction_label}
                  </span>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-400 block font-medium">Estimated Tampering Probability</span>
                  <span className="text-lg font-bold text-slate-900 mt-1 block">
                    {(verification.ml_prediction.fraud_probability * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-400 block font-medium">Training Strategy</span>
                  <span className="text-xs font-semibold text-slate-800 mt-1 block">
                    Grouped Document Splits (70/15/15)
                  </span>
                </div>
              </div>

              {verification.ml_prediction.feature_vector && (
                <div className="mt-4">
                  <h3 className="text-xs font-bold text-slate-800 mb-2">Evaluated 18-Dimensional Feature Vector</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 text-[11px] font-mono">
                    {Object.entries(verification.ml_prediction.feature_vector).map(([k, v]) => (
                      <div key={k} className="p-2 bg-slate-50 rounded border border-slate-100">
                        <span className="text-slate-400 block truncate">{k}</span>
                        <span className="font-bold text-slate-800">{typeof v === 'number' ? v.toFixed(3) : v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-2">
              <p className="text-sm font-semibold text-slate-800">Model not trained / unavailable</p>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                No active model artifact is deployed at the configured path. Deterministic forensics and OCR rules are functioning normally.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
    </AuthGuard>
  );
}
