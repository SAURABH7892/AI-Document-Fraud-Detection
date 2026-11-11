'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileText, Search, Trash2, Download, ExternalLink, ArrowUpRight,
  RefreshCw, Filter, ShieldCheck, AlertTriangle, ShieldAlert
} from 'lucide-react';
import { api } from '@/lib/api';
import { DocumentItem } from '@/types';
import { AuthGuard } from '@/components/AuthGuard';

export default function HistoryPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchDocs = async (query = '') => {
    setLoading(true);
    try {
      const data = await api.listDocuments(query);
      setDocuments(data);
    } catch (err: any) {
      if (err.message === 'Not authenticated') {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs(search);
  }, [search]);

  const handleDelete = async (id: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}" and all its forensic findings?`)) {
      return;
    }
    setDeletingId(id);
    try {
      await api.deleteDocument(id);
      setDocuments(documents.filter((d) => d.id !== id));
    } catch (err) {
      alert('Failed to delete document');
    } finally {
      setDeletingId(null);
    }
  };

  const filteredDocs = documents.filter((d) => {
    if (statusFilter === 'ALL') return true;
    return d.status === statusFilter;
  });

  return (
    <AuthGuard>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Audit & Verification History</h1>
          <p className="text-xs text-slate-500 mt-1">Review previously analyzed academic credentials and reports</p>
        </div>

        <button
          onClick={() => fetchDocs(search)}
          className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors self-start sm:self-auto"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search documents by filename..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-900"
          />
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-500 font-medium">Status:</span>
          {['ALL', 'COMPLETED', 'PROCESSING', 'FAILED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-sky-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading history records...</div>
        ) : filteredDocs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-6">Document Name</th>
                  <th className="py-3 px-6">Format</th>
                  <th className="py-3 px-6">File Size</th>
                  <th className="py-3 px-6">Analysis Status</th>
                  <th className="py-3 px-6">Created Date</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-6 font-semibold text-slate-900 max-w-xs truncate">
                      <Link href={`/documents/${doc.id}`} className="hover:text-sky-600 transition-colors">
                        {doc.original_filename}
                      </Link>
                    </td>
                    <td className="py-3.5 px-6 text-slate-500 uppercase">{doc.mime_type.split('/')[1]}</td>
                    <td className="py-3.5 px-6 text-slate-500">{(doc.file_size_bytes / 1024).toFixed(1)} KB</td>
                    <td className="py-3.5 px-6">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded text-[10px] font-semibold border ${
                          doc.status === 'COMPLETED'
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : doc.status === 'FAILED'
                            ? 'bg-rose-50 text-rose-700 border-rose-200'
                            : 'bg-amber-50 text-amber-700 border-amber-200'
                        }`}
                      >
                        {doc.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-slate-500">
                      {new Date(doc.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-6 text-right space-x-2">
                      {doc.status === 'COMPLETED' && (
                        <a
                          href={api.getReportDownloadByDocUrl(doc.id)}
                          download
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-slate-700 hover:text-sky-600 font-semibold px-2 py-1 rounded border border-slate-200 hover:border-sky-300 bg-slate-50 hover:bg-sky-50/50 transition-colors"
                          title="Download Official PDF Report"
                        >
                          <Download className="w-3.5 h-3.5 text-sky-600" />
                          <span>Report PDF</span>
                        </a>
                      )}
                      <Link
                        href={`/documents/${doc.id}`}
                        className="inline-flex items-center gap-1 text-sky-600 hover:text-sky-800 font-semibold"
                      >
                        Inspect <ArrowUpRight className="w-3.5 h-3.5" />
                      </Link>
                      <button
                        onClick={() => handleDelete(doc.id, doc.original_filename)}
                        disabled={deletingId === doc.id}
                        className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                        title="Delete record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-xs text-slate-400">
            No verification records matching current filters.
          </div>
        )}
      </div>
    </div>
    </AuthGuard>
  );
}
