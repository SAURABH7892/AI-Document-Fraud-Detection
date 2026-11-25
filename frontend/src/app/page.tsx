import React from 'react';
import Link from 'next/link';
import {
  Shield, CheckCircle2, AlertTriangle, FileSearch, Cpu, Lock,
  ArrowRight, FileCheck, Layers, Eye, ScanLine, Scale
} from 'lucide-react';

export default function LandingPage() {
  const workflowSteps = [
    {
      step: '01',
      title: 'Secure Upload & Validation',
      desc: 'MIME, magic header bytes, and SHA-256 cryptographic digest verified before storage.',
      icon: Lock,
    },
    {
      step: '02',
      title: 'PDF & Page Preprocessing',
      desc: 'Multi-page PDF rendering via PyMuPDF at 200+ DPI with adaptive grayscale normalization.',
      icon: Layers,
    },
    {
      step: '03',
      title: 'OCR & Academic Field Extraction',
      desc: 'Extracts student name, institution, roll number, degree, date, and grade/CGPA with coordinates.',
      icon: ScanLine,
    },
    {
      step: '04',
      title: 'Computer Vision & ELA Forensics',
      desc: 'Error Level Analysis (ELA), Laplacian noise inconsistency index, and text baseline alignment.',
      icon: Eye,
    },
    {
      step: '05',
      title: 'Supervised ML Risk Engine',
      desc: 'Classifies multi-signal 18-dim feature vector and aggregates into calibrated risk tiers.',
      icon: Cpu,
    },
    {
      step: '06',
      title: 'Audit-Ready PDF Report',
      desc: 'Generates formal ReportLab verification report with findings, limitations, and review recommendation.',
      icon: FileCheck,
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-sky-900 via-slate-900 to-slate-950 text-white py-24 px-4 sm:px-6 lg:px-8">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]" />
        
        <div className="relative max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-500/10 border border-sky-400/30 text-sky-300 text-xs font-semibold mb-8 backdrop-blur-sm">
            <Shield className="w-4 h-4 text-sky-400" />
            Major Project 2026–27 · Academic Credential Integrity Platform
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight sm:leading-tight mb-6">
            AI-Based Document Fraud Detection <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-300">
              & Verification System
            </span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-lg text-slate-300 leading-relaxed mb-10 font-normal">
            DocShield AI combines high-resolution OCR, Error Level Analysis (ELA), localized noise inconsistency detection,
            and supervised machine learning to assist organizations in screening academic degrees and mark sheets for digital tampering.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/upload"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-sm shadow-lg shadow-sky-500/25 transition-all hover:scale-[1.02]"
            >
              <FileSearch className="w-4 h-4" />
              Upload & Screen Document
            </Link>
            <Link
              href="/dashboard"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-white font-medium text-sm transition-all"
            >
              Open Dashboard
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </Link>
          </div>

          {/* Quick Demo Info */}
          <div className="mt-12 p-3 bg-slate-800/40 border border-slate-700/60 rounded-xl inline-flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400">
            <span>Demo Account: <strong className="text-slate-200">demo@docshield.ai</strong></span>
            <span>Password: <strong className="text-slate-200">DemoPass123!</strong></span>
            <span className="text-sky-400 font-medium">Ready for immediate testing</span>
          </div>
        </div>
      </section>

      {/* Core Workflow Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest mb-2">Multimodal Analysis Pipeline</h2>
          <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">How DocShield Analyzes Academic Documents</h3>
          <p className="mt-3 text-sm text-slate-600">
            Rather than relying on a single fallible indicator, DocShield aggregates multiple independent forensics checks into an explainable decision.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflowSteps.map((item, index) => {
            const Icon = item.icon;
            return (
              <div key={index} className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-shadow relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center font-bold border border-sky-100">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-extrabold text-slate-300 font-mono">{item.step}</span>
                </div>
                <h4 className="text-base font-bold text-slate-900 mb-2">{item.title}</h4>
                <p className="text-xs text-slate-600 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Domain Scope & Integrity Policy */}
      <section className="bg-slate-100 border-y border-slate-200 py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-sky-100 text-sky-800 text-xs font-semibold mb-3">
              <Scale className="w-3.5 h-3.5" /> Scope & Transparency Principles
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-4 tracking-tight">
              Honest Verification, Transparent Limitations
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              Our system strictly distinguishes <strong>AI-assisted integrity assessment</strong> from official 
              <strong>issuer-backed legal verification</strong>. We never claim visual analysis alone proves a document legally authentic.
            </p>
            <ul className="space-y-2.5 text-xs text-slate-700">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Initial Domain:</strong> Academic degrees, mark sheets, and provisional university diplomas (PDF, JPG, PNG).</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>No Fake Metrics:</strong> Grounded risk calculations derived from actual extracted features and validated models.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span><strong>Human Review Workflow:</strong> Flags high-risk cases for manual inspection with highlighted anomaly coordinates.</span>
              </li>
            </ul>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Academic Disclaimer
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              Error Level Analysis, compression discrepancies, and font variances can occasionally be introduced by scanner hardware,
              re-saving, or PDF compilation. Findings should be treated as investigatory indicators to prioritize manual review.
            </p>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500">
              <span className="font-semibold text-slate-700 block mb-1">Project Authors</span>
              Vaibhav (AI/ML & Backend Lead) · Saurabh (Full-Stack & Deployment Lead)
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
