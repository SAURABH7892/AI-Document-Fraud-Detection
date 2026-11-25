import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert, HelpCircle } from 'lucide-react';

interface RiskBadgeProps {
  level: 'LOW_RISK' | 'MEDIUM_RISK' | 'HIGH_RISK' | 'INCONCLUSIVE' | string;
  score?: number;
  showScore?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, showScore = false }) => {
  switch (level) {
    case 'LOW_RISK':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          Low Risk {showScore && score !== undefined ? `(${score.toFixed(1)}/100)` : ''}
        </span>
      );
    case 'MEDIUM_RISK':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          Medium Risk {showScore && score !== undefined ? `(${score.toFixed(1)}/100)` : ''}
        </span>
      );
    case 'HIGH_RISK':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
          High Risk {showScore && score !== undefined ? `(${score.toFixed(1)}/100)` : ''}
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-300">
          <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
          Inconclusive
        </span>
      );
  }
};
