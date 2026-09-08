var API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:5000/api'
  : 'https://ai-resume-builder-backend-i337.onrender.com/api';

const API = {
 
  async _request(path, options = {}) {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
        ...options,
      });
      const data = await res.json();
      if (!res.ok) return { error: data.error || 'Something went wrong.' };
      return data;
    } catch (err) {
      return { error: 'Network error. Is the server running?' };
    }
  },

  // ── Auth ──────────────────────────────────────────────────────────
  register: (body)  => API._request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login:    (body)  => API._request('/auth/login',    { method: 'POST', body: JSON.stringify(body) }),
  logout:   ()      => API._request('/auth/logout',   { method: 'POST' }),
  me:       ()      => API._request('/auth/me'),
  verifyEmail: (token) => API._request(`/auth/verify/${token}`),

  // ── Upload (multipart) ────────────────────────────────────────────
  async upload(file, jobTitle, jobDesc) {
    const form = new FormData();
    form.append('resume', file);
    form.append('job_title', jobTitle);
    form.append('job_desc', jobDesc);
    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        credentials: 'include',
        body: form,
      });
      const data = await res.json();
      if (!res.ok) return { error: data.error || 'Upload failed.' };
      return data;
    } catch {
      return { error: 'Upload failed. Check your connection.' };
    }
  },

  // ── History ───────────────────────────────────────────────────────
  getHistory: () => API._request('/history'),

  // ── Admin ─────────────────────────────────────────────────────────
  getAdminUsers:          ()               => API._request('/admin/users'),
  getAdminUserResumes:    (userId)         => API._request(`/admin/users/${userId}/resumes`),
  getAdminActivity:       (from, to)       => {
    const params = new URLSearchParams();
    if (from) params.set('from', from);
    if (to)   params.set('to', to);
    return API._request(`/admin/activity?${params.toString()}`);
  },
};