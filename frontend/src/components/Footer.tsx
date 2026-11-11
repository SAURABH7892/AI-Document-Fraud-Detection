import React from 'react';
import { Shield, Lock, FileCheck } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 text-xs border-t border-slate-800 mt-auto py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center border border-sky-500/30">
                <Shield className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-100 text-sm">DocShield AI</span>
            </div>
            <p className="text-slate-400 leading-relaxed max-w-md text-xs">
              AI-assisted web platform for document integrity screening, digital forensics,
              Error Level Analysis (ELA), and automated verification reporting for academic credentials.
            </p>
          </div>

          <div>
            <span className="font-semibold text-slate-200 block mb-2.5">Project Information</span>
            <ul className="space-y-1.5 text-slate-400">
              <li>Major Project Review: Session 2026–27</li>
              <li>AI/ML & Backend Lead: <span className="text-slate-300">Vaibhav</span></li>
              <li>Full-Stack & Deployment Lead: <span className="text-slate-300">Saurabh</span></li>
              <li>Domain: Academic Certificates & Mark Sheets</li>
            </ul>
          </div>

          <div>
            <span className="font-semibold text-slate-200 block mb-2.5">Integrity & Compliance</span>
            <p className="text-slate-400 leading-normal text-xs">
              Automated image forensics and ML provide decision support. They do not constitute sole legal certification of authenticity.
            </p>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px]">
          <p>© 2026–2027 DocShield AI. B.Tech Computer Science Major Project.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Lock className="w-3 h-3 text-slate-500" /> End-to-End Isolated Processing
            </span>
            <span className="flex items-center gap-1">
              <FileCheck className="w-3 h-3 text-slate-500" /> ReportLab Verification Engine
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
