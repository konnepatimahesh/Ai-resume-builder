(async () => {
  const user = await guardAuth();
  if (!user) return;
  initNavbar(user);

  const result = await API.getHistory();

  if (result.error) {
    showToast(result.error, 'error');
    return;
  }

  const list = result.history || [];
  const badge = document.getElementById('totalBadge');
  badge.textContent = `${list.length} session${list.length !== 1 ? 's' : ''}`;

  const tbody = document.getElementById('historyBody');

  if (list.length === 0) {
    document.getElementById('tableWrapper').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
    return;
  }

  tbody.innerHTML = list.map((h, i) => {
    const score = h.ats_score != null ? h.ats_score.toFixed(0) : null;
    const scoreBadge = score
      ? `<span class="badge" style="background:${scoreColor(score)};color:#fff">${score}% ${scoreLabel(score)}</span>`
      : '<span class="text-muted">—</span>';

    const pdfLink  = h.pdf_path
      ? `<a href="/outputs/${h.pdf_path}" target="_blank" class="btn btn-ghost btn-sm">PDF</a>`
      : '';
    const docxLink = h.docx_path
      ? `<a href="/outputs/${h.docx_path}" target="_blank" class="btn btn-ghost btn-sm">DOCX</a>`
      : '';

    const viewBtn = `<button class="btn btn-primary btn-sm" onclick="viewSession(${h.id}, '${h.uploaded_file_path.replace(/'/g, "\\'")}', '${(h.job_title || '').replace(/'/g, "\\'")}')">📊 View Report</button>`;

    return `
      <tr>
        <td class="text-muted">${i + 1}</td>
        <td><strong>${h.job_title || 'Untitled'}</strong></td>
        <td>${scoreBadge}</td>
        <td>${formatDateTime(h.created_at)}</td>
        <td>
          <div class="d-flex align-center gap-1">
            ${viewBtn}
            ${pdfLink}
            ${docxLink}
          </div>
        </td>
      </tr>`;
  }).join('');
})();

function viewSession(id, filename, jobTitle) {
  sessionStorage.clear();
  sessionStorage.setItem('history_id', id);
  sessionStorage.setItem('filename', filename);
  sessionStorage.setItem('job_title', jobTitle);
  sessionStorage.setItem('job_desc', 'HISTORICAL');
  window.location.href = 'report.html';
}