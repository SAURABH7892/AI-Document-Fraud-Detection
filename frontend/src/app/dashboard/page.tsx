'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileText, CheckCircle2, Clock, AlertTriangle, UploadCloud,
  ChevronRight, ShieldAlert, ShieldCheck, ArrowUpRight, RefreshCw
} from 'lucide-react';
import { api } from '@/lib/api';
import { DashboardStats } from '@/types';
import { StatCard } from '@/components/StatCard';
import { RiskBadge } from '@/components/RiskBadge';
import { AuthGuard } from '@/components/AuthGuard';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      if (err.message === 'Not authenticated') {
        router.push('/login');
      } else {
        setError(err.message || 'Failed to load dashboard metrics');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <AuthGuard>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-slate-200 rounded w-1/4" />
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-28 bg-slate-200 rounded-xl" />
              ))}
            </div>
            <div className="h-64 bg-slate-200 rounded-xl" />
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Security & Integrity Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">Real-time academic credential screening metrics and audit logs</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchStats}
            className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            title="Refresh metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs shadow-sm transition-colors"
          >
            <UploadCloud className="w-4 h-4" />
            Screen New Document
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs">
          {error}
        </div>
      )}

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Documents"
          value={stats?.total_documents || 0}
          subtitle="Uploaded in your repository"
          icon={<FileText className="w-5 h-5 text-sky-600" />}
        />
        <StatCard
          title="Completed Verifications"
          value={stats?.completed_verifications || 0}
          subtitle="Forensic analysis executed"
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-600" />}
        />
        <StatCard
          title="In Queue / Processing"
          value={stats?.pending_jobs || 0}
          subtitle="Background AI worker jobs"
          icon={<Clock className="w-5 h-5 text-amber-600" />}
        />
        <StatCard
          title="Elevated Risk Flags"
          value={stats?.risk_distribution?.HIGH_RISK || 0}
          subtitle="High anomaly alerts detected"
          icon={<ShieldAlert className="w-5 h-5 text-rose-600" />}
        />
      </div>

      {/* Risk Distribution Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-sm font-bold text-slate-900 mb-4">Risk Level Distribution</h2>
          {stats && (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-emerald-700 flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> Low Risk (Authentic)
                  </span>
                  <span className="font-bold text-slate-800">{stats.risk_distribution.LOW_RISK}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-emerald-500 h-2 rounded-full"
                    style={{
                      width: `${stats.completed_verifications ? (stats.risk_distribution.LOW_RISK / stats.completed_verifications) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-amber-700 flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Medium Risk (Review)
                  </span>
                  <span className="font-bold text-slate-800">{stats.risk_distribution.MEDIUM_RISK}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-amber-500 h-2 rounded-full"
                    style={{
                      width: `${stats.completed_verifications ? (stats.risk_distribution.MEDIUM_RISK / stats.completed_verifications) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-rose-700 flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" /> High Risk (Tampered)
                  </span>
                  <span className="font-bold text-slate-800">{stats.risk_distribution.HIGH_RISK}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-rose-500 h-2 rounded-full"
                    style={{
                      width: `${stats.completed_verifications ? (stats.risk_distribution.HIGH_RISK / stats.completed_verifications) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-slate-600 flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-400 inline-block" /> Inconclusive
                  </span>
                  <span className="font-bold text-slate-800">{stats.risk_distribution.INCONCLUSIVE}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-slate-400 h-2 rounded-full"
                    style={{
                      width: `${stats.completed_verifications ? (stats.risk_distribution.INCONCLUSIVE / stats.completed_verifications) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recent Documents Table */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-900">Recent Verification Records</h2>
            <Link href="/history" className="text-xs text-sky-600 hover:text-sky-700 font-semibold flex items-center gap-1">
              View all history <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {stats?.recent_documents && stats.recent_documents.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-400 font-medium">
                    <th className="pb-3">Filename</th>
                    <th className="pb-3">Format</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Date</th>
                    <th className="pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {stats.recent_documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 font-medium text-slate-800 max-w-[180px] truncate">
                        {doc.original_filename}
                      </td>
                      <td className="py-3 text-slate-500 uppercase">{doc.mime_type.split('/')[1]}</td>
                      <td className="py-3">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                            doc.status === 'COMPLETED'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : doc.status === 'FAILED'
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : 'bg-amber-50 text-amber-700 border border-amber-200'
                          }`}
                        >
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-3 text-slate-500">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 text-right">
                        <Link
                          href={`/documents/${doc.id}`}
                          className="inline-flex items-center gap-1 text-sky-600 hover:text-sky-800 font-semibold text-xs"
                        >
                          Inspect <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-400 text-xs">
              No documents processed yet. Upload your first academic certificate to begin.
            </div>
          )}
        </div>
      </div>
    </div>
    </AuthGuard>
  );
}
