// API_BASE is declared in api.js

// ── Toast notifications ──────────────────────────────────────────────
function showToast(message, type = 'default', duration = 3500) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut .25s ease forwards';
    setTimeout(() => toast.remove(), 260);
  }, duration);
}

// ── Form error helpers ───────────────────────────────────────────────
function showFieldErr(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
}

function clearErrors() {
  document.querySelectorAll('.form-error').forEach(el => {
    el.textContent = '';
    el.classList.add('hidden');
  });
  document.querySelectorAll('.form-control').forEach(el => el.classList.remove('error'));
}

// ── Password toggle ──────────────────────────────────────────────────
function togglePwd(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isText = input.type === 'text';
  input.type = isText ? 'password' : 'text';
  btn.textContent = isText ? '👁' : '🙈';
}

// ── Date formatting ──────────────────────────────────────────────────
function formatDate(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric'
  });
}

function formatDateTime(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

// ── Score color ──────────────────────────────────────────────────────
function scoreColor(score) {
  if (score >= 80) return 'var(--success)';
  if (score >= 60) return 'var(--warning)';
  return 'var(--danger)';
}

function scoreLabel(score) {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Needs Work';
}

// ── Auth guard ───────────────────────────────────────────────────────
async function getCurrentUser() {
  try {
    const res = await fetch(`${API_BASE}/auth/me`, { credentials: 'include' });
    if (!res.ok) return null;
    const data = await res.json();
    return data.user || null;
  } catch {
    return null;
  }
}

async function guardAuth(requiredRole = null) {
  const user = await getCurrentUser();
  if (!user) {
    window.location.href = 'login.html';
    return null;
  }
  if (requiredRole && user.role !== requiredRole) {
    showToast('Access denied.', 'error');
    window.location.href = 'dashboard.html';
    return null;
  }
  return user;
}

// ── Logout ───────────────────────────────────────────────────────────
async function handleLogout() {
  await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
  window.location.href = 'login.html';
}

// ── Navbar init ──────────────────────────────────────────────────────
function initNavbar(user) {
  const nameEl   = document.getElementById('navName');
  const avatarEl = document.getElementById('navAvatar');
  if (nameEl)   nameEl.textContent   = user.name;
  if (avatarEl) avatarEl.textContent = user.name.charAt(0).toUpperCase();
}

function showTab(tabName) {
  // Simple tab switcher used in admin
  const allTabs = document.querySelectorAll('[id^="tab"]');
  allTabs.forEach(t => t.classList.add('hidden'));
  const target = document.getElementById(`tab${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`);
  if (target) target.classList.remove('hidden');
}