const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

function getAuthHeader(): Record<string, string> {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('docshield_token');
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

export const api = {
  // Auth
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Authentication failed');
    }
    return res.json();
  },

  async register(fullName: string, email: string, password: string) {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: fullName, email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Not authenticated');
    return res.json();
  },

  // Dashboard
  async getDashboardStats() {
    const res = await fetch(`${API_BASE}/api/v1/dashboard/stats`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to load dashboard statistics');
    return res.json();
  },

  // Documents
  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', 'academic_certificate');

    const res = await fetch(`${API_BASE}/api/v1/documents`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async listDocuments(search = '') {
    const url = search 
      ? `${API_BASE}/api/v1/documents?search=${encodeURIComponent(search)}`
      : `${API_BASE}/api/v1/documents`;
    const res = await fetch(url, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async getDocument(id: string) {
    const res = await fetch(`${API_BASE}/api/v1/documents/${id}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Document not found');
    return res.json();
  },

  async deleteDocument(id: string) {
    const res = await fetch(`${API_BASE}/api/v1/documents/${id}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
  },

  async getJobStatus(documentId: string) {
    const res = await fetch(`${API_BASE}/api/v1/documents/${documentId}/job`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Failed to fetch job status');
    return res.json();
  },

  // Verifications
  async getVerificationByDocument(documentId: string) {
    const res = await fetch(`${API_BASE}/api/v1/verifications/by-document/${documentId}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error('Verification not ready or not found');
    return res.json();
  },

  getReportDownloadUrl(verificationId: string) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('docshield_token') : null;
    const base = `${API_BASE}/api/v1/verifications/${verificationId}/report`;
    return token ? `${base}?token=${encodeURIComponent(token)}` : base;
  },

  getReportDownloadByDocUrl(documentId: string) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('docshield_token') : null;
    const base = `${API_BASE}/api/v1/verifications/documents/${documentId}/report`;
    return token ? `${base}?token=${encodeURIComponent(token)}` : base;
  },

  getElaArtifactUrl(documentId: string) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('docshield_token') : null;
    const base = `${API_BASE}/api/v1/verifications/documents/${documentId}/artifacts/ela`;
    return token ? `${base}?token=${encodeURIComponent(token)}` : base;
  },

  getOriginalFileUrl(documentId: string) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('docshield_token') : null;
    const base = `${API_BASE}/api/v1/documents/${documentId}/file`;
    return token ? `${base}?token=${encodeURIComponent(token)}` : base;
  }
};
