// ── Mode helpers ──────────────────────────────────────────────
function getGrade() { return localStorage.getItem('sb_grade') || 'college'; }

function getMode() {
  const g = getGrade();
  if (g === 'college') return 'college';
  const n = parseInt(g);
  return n <= 5 ? 'primary' : 'secondary';
}

function getGradeLabel() {
  const g = getGrade();
  return g === 'college' ? 'College' : 'Grade ' + g;
}

function getModeEmoji() {
  const m = getMode();
  return m === 'primary' ? '🎒' : m === 'secondary' ? '📚' : '🎓';
}

// Apply body class + update sidebar grade chip on every page
document.addEventListener('DOMContentLoaded', () => {
  const mode = getMode();
  document.body.classList.add('mode-' + mode);

  const chip = document.getElementById('gradeChip');
  if (chip) chip.textContent = getGradeLabel();

  const modeEmoji = document.getElementById('modeEmoji');
  if (modeEmoji) modeEmoji.textContent = getModeEmoji();

  // If no grade set, redirect to mode selection (skip if already on that page)
  if (!localStorage.getItem('sb_grade') && !window.location.pathname.includes('mode-select')) {
    window.location.href = '/mode-select';
  }
});

// ── UI helpers ────────────────────────────────────────────────
function setLoading(btn, loading, html) {
  btn.disabled = loading;
  btn.innerHTML = html;
}

function showToast(message, type = 'success') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icon = type === 'success' ? 'fa-circle-check' : 'fa-triangle-exclamation';
  toast.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut .25s ease forwards';
    setTimeout(() => toast.remove(), 260);
  }, 3000);
}

// ── Markdown → HTML ───────────────────────────────────────────
function mdToHtml(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/^• (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/\n/g, '<br>');
}
