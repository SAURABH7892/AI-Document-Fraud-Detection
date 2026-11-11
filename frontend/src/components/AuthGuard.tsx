'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Shield, RefreshCw } from 'lucide-react';

interface AuthGuardProps {
  children: React.ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    // Check if authentication token exists in localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('docshield_token') : null;
    
    if (!token) {
      setIsAuthenticated(false);
      // Redirect to login with return path
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
    } else {
      setIsAuthenticated(true);
    }
  }, [pathname, router]);

  // Loading state while checking authentication
  if (isAuthenticated === null) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 bg-sky-50 text-sky-600 rounded-2xl flex items-center justify-center border border-sky-100 shadow-sm animate-pulse">
          <Shield className="w-6 h-6" />
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
          <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-600" />
          <span>Verifying access credentials...</span>
        </div>
      </div>
    );
  }

  // If not authenticated, return null while redirect takes effect
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
};
