let allUsers = [];

(async () => {
  const user = await guardAuth('admin');
  if (!user) return;
  initNavbar(user);

  await loadUsers();
  await loadActivity();
})();

async function loadUsers() {
  const result = await API.getAdminUsers();
  if (result.error) { showToast(result.error, 'error'); return; }

  allUsers = result.users || [];

  document.getElementById('statUsers').textContent    = allUsers.length;
  document.getElementById('statVerified').textContent = allUsers.filter(u => u.is_verified).length;

  renderUsersTable(allUsers);
}

function renderUsersTable(users) {
  const tbody = document.getElementById('usersBody');
  if (users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted" style="padding:2rem">No users found.</td></tr>';
    return;
  }

  tbody.innerHTML = users.map(u => `
    <tr>
      <td class="text-muted">${u.id}</td>
      <td><strong>${u.name}</strong></td>
      <td>${u.email}</td>
      <td><span class="admin-tag ${u.role === 'admin' ? 'admin-role' : 'user-role'}">${u.role}</span></td>
      <td>${u.is_verified
        ? '<span class="badge badge-success">✓ Verified</span>'
        : '<span class="badge badge-danger">✗ Pending</span>'}</td>
      <td>${formatDate(u.created_at)}</td>
      <td><button class="view-btn" onclick="openResumeModal(${u.id}, '${u.name.replace(/'/g,"\\'")}')">View Resumes</button></td>
    </tr>`).join('');
}

function filterUsers(query) {
  const q = query.toLowerCase();
  const filtered = allUsers.filter(u =>
    u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
  );
  renderUsersTable(filtered);
}

async function openResumeModal(userId, userName) {
  document.getElementById('modalUserName').textContent = userName;
  document.getElementById('resumeModal').classList.remove('hidden');
  document.getElementById('resumeBody').innerHTML =
    '<tr><td colspan="4" class="text-center text-muted">Loading…</td></tr>';

  const result = await API.getAdminUserResumes(userId);
  if (result.error) {
    document.getElementById('resumeBody').innerHTML =
      `<tr><td colspan="4" class="text-center text-muted">${result.error}</td></tr>`;
    return;
  }

  const list = result.resumes || [];
  if (list.length === 0) {
    document.getElementById('resumeBody').innerHTML =
      '<tr><td colspan="4" class="text-center text-muted">No resumes uploaded yet.</td></tr>';
    return;
  }

  document.getElementById('resumeBody').innerHTML = list.map(r => {
    const score = r.ats_score != null ? r.ats_score.toFixed(0) + '%' : '—';
    const pdf  = r.pdf_path  ? `<a href="${API_BASE.replace('/api', '')}/outputs/${r.pdf_path}"  target="_blank" class="btn btn-ghost btn-sm">PDF</a>`  : '';
    const docx = r.docx_path ? `<a href="${API_BASE.replace('/api', '')}/outputs/${r.docx_path}" target="_blank" class="btn btn-ghost btn-sm">DOCX</a>` : '';
    return `<tr>
      <td>${r.job_title || 'Untitled'}</td>
      <td><span class="badge" style="background:${scoreColor(parseFloat(r.ats_score)||0)};color:#fff">${score}</span></td>
      <td>${formatDateTime(r.created_at)}</td>
      <td class="d-flex gap-1">${pdf}${docx || '<span class="text-muted text-sm">—</span>'}</td>
    </tr>`;
  }).join('');

  document.getElementById('statAnalyses').textContent =
    (parseInt(document.getElementById('statAnalyses').textContent) || 0) + list.length;
}

function closeResumeModal() {
  document.getElementById('resumeModal').classList.add('hidden');
}

async function loadActivity() {
  const from = document.getElementById('fromDate')?.value || '';
  const to   = document.getElementById('toDate')?.value   || '';
  const result = await API.getAdminActivity(from, to);

  document.getElementById('statLogs').textContent = result.logs ? result.logs.length : 0;

  const tbody = document.getElementById('activityBody');
  if (result.error) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">${result.error}</td></tr>`;
    return;
  }

  const logs = result.logs || [];
  if (logs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted" style="padding:2rem">No activity in this range.</td></tr>';
    return;
  }

  tbody.innerHTML = logs.map(l => `
    <tr>
      <td><strong>${l.user_name}</strong></td>
      <td>${l.user_email}</td>
      <td>${l.query_text || '—'}</td>
      <td>${formatDateTime(l.timestamp)}</td>
    </tr>`).join('');
}

function clearFilter() {
  document.getElementById('fromDate').value = '';
  document.getElementById('toDate').value   = '';
  loadActivity();
}