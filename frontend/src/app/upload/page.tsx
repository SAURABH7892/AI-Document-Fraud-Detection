'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { UploadCloud, File, AlertCircle, CheckCircle2, ArrowRight, Shield, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import { AuthGuard } from '@/components/AuthGuard';

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadedDocId, setUploadedDocId] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    setError(null);
    setUploadedDocId(null);
    const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
    const lowerName = file.name.toLowerCase();
    const isValidExt = validExtensions.some((ext) => lowerName.endsWith(ext));

    if (!isValidExt) {
      setError('Unsupported file type. Only PDF, JPG, JPEG, and PNG files are supported.');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError('File size exceeds the 15 MB limit.');
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setUploadProgress(20);

    try {
      setUploadProgress(50);
      const res = await api.uploadDocument(selectedFile);
      setUploadProgress(100);
      setUploadedDocId(res.id);

      // Auto redirect to document details after 1.5 seconds
      setTimeout(() => {
        router.push(`/documents/${res.id}`);
      }, 1200);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setUploading(false);
    }
  };

  return (
    <AuthGuard>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center max-w-xl mx-auto mb-8">
        <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto mb-3 border border-sky-100">
          <UploadCloud className="w-5 h-5" />
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Upload Academic Document</h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload degrees, transcripts, or mark sheets (PDF, JPG, PNG) for forensic analysis
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
        {/* Drag and Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
            dragActive
              ? 'border-sky-500 bg-sky-50/50'
              : 'border-slate-300 hover:border-sky-400 bg-slate-50/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            className="hidden"
            onChange={handleFileInputChange}
          />

          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-sky-100 text-sky-600 flex items-center justify-center">
              <UploadCloud className="w-7 h-7" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">
                Click to browse or drag & drop document
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supported formats: PDF, JPG, JPEG, PNG (Max file size: 15 MB)
              </p>
            </div>
          </div>
        </div>

        {/* Selected File Card */}
        {selectedFile && (
          <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center">
                <File className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900 truncate max-w-sm">{selectedFile.name}</p>
                <p className="text-[11px] text-slate-500">
                  {(selectedFile.size / 1024).toFixed(1)} KB · {selectedFile.type || 'Document'}
                </p>
              </div>
            </div>

            <button
              onClick={() => setSelectedFile(null)}
              className="text-xs text-slate-400 hover:text-rose-600 transition-colors font-medium"
            >
              Remove
            </button>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2 text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Alert */}
        {uploadedDocId && (
          <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2 text-emerald-700 text-xs">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>Document accepted! Initiating background forensic screening pipeline...</span>
          </div>
        )}

        {/* Progress Bar */}
        {uploading && (
          <div className="mt-6 space-y-2">
            <div className="flex justify-between text-xs text-slate-600 font-medium">
              <span>Uploading & hashing file...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-sky-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-6">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="w-full py-3 px-4 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-semibold text-sm shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Processing Upload...
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                Dispatch to Forensics & OCR Engine
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
    </AuthGuard>
  );
}
