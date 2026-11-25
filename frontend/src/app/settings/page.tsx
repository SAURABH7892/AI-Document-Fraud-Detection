'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, User, Lock, Database, Info, HardDrive, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';
import { User as UserType } from '@/types';
import { AuthGuard } from '@/components/AuthGuard';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserType | null>(null);

  useEffect(() => {
    api.getMe()
      .then(setUser)
      .catch(() => router.push('/login'));
  }, []);

  return (
    <AuthGuard>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">System & Account Settings</h1>
        <p className="text-xs text-slate-500 mt-1">Manage user preferences, data retention controls, and review engine configuration</p>
      </div>

      {/* Account Profile Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <User className="w-4 h-4 text-sky-600" />
          Reviewer Profile Information
        </h2>
        {user ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block font-medium mb-1">Full Name</span>
              <span className="text-sm font-semibold text-slate-800">{user.full_name}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium mb-1">Email Address</span>
              <span className="text-sm font-semibold text-slate-800">{user.email}</span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium mb-1">Assigned Role</span>
              <span className="inline-block px-2.5 py-0.5 rounded text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-200 capitalize">
                {user.role}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block font-medium mb-1">Account Created</span>
              <span className="text-slate-600">{new Date(user.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-400">Loading user profile...</p>
        )}
      </div>

      {/* Security & Retention Policy */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Lock className="w-4 h-4 text-sky-600" />
          Privacy & Document Retention Policy
        </h2>
        <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
          <p>
            • <strong>Isolated Document Directories:</strong> Uploaded certificates are indexed with UUID identifiers
            in secure, isolated processing directories. No shared filenames are used across concurrent jobs.
          </p>
          <p>
            • <strong>User Ownership Enforcement:</strong> Access control checks are applied to all API endpoints.
            Documents, ELA artifacts, and PDF reports can only be retrieved by their authorized creator.
          </p>
          <p>
            • <strong>Permanent User-Initiated Deletion:</strong> Deleting a record from the history table removes both the
            database metadata and the underlying stored artifacts on disk.
          </p>
        </div>
      </div>

      {/* Engine & Configuration Overview */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-sky-600" />
          Forensic Engine Capabilities
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">OCR Extraction Service</span>
            <span className="font-semibold text-slate-800 mt-1 block">PyMuPDF Vector Streams + Layout Contours</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">Digital Forensics Module</span>
            <span className="font-semibold text-slate-800 mt-1 block">Error Level Analysis (ELA) + Laplacian Variance</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">ML Model Architecture</span>
            <span className="font-semibold text-slate-800 mt-1 block">Random Forest Classifier (18 Features)</span>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">Government Issuer API</span>
            <span className="font-semibold text-amber-700 mt-1 block">DigiLocker / NAD: Not Configured (Inactive)</span>
          </div>
        </div>
      </div>

      {/* Academic Credits */}
      <div className="p-4 bg-sky-50 border border-sky-200 rounded-xl text-xs text-sky-900 flex items-start gap-3">
        <Info className="w-5 h-5 text-sky-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold block mb-1">B.Tech Major Project Review — Session 2026–27</span>
          <p className="leading-relaxed">
            Team Members: <strong>Vaibhav</strong> (AI/ML & Backend Lead) & <strong>Saurabh</strong> (Full-Stack & Deployment Lead).
            Developed under major project guidelines for automated document integrity screening.
          </p>
        </div>
      </div>
    </div>
    </AuthGuard>
  );
}
