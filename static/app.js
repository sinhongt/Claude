// Shared state
const AppState = {
  get sessionId() { return localStorage.getItem('sessionId'); },
  set sessionId(v) { v ? localStorage.setItem('sessionId', v) : localStorage.removeItem('sessionId'); },
  get book() { return JSON.parse(localStorage.getItem('book') || 'null'); },
  set book(v) { v ? localStorage.setItem('book', JSON.stringify(v)) : localStorage.removeItem('book'); },
  get character() { return JSON.parse(localStorage.getItem('character') || 'null'); },
  set character(v) { v ? localStorage.setItem('character', JSON.stringify(v)) : localStorage.removeItem('character'); },
  get chapters() { return JSON.parse(localStorage.getItem('chapters') || '[]'); },
  set chapters(v) { localStorage.setItem('chapters', JSON.stringify(v)); },
};

async function apiPost(endpoint, body) {
  const resp = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}

async function apiGet(endpoint) {
  const resp = await fetch(endpoint);
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}

function showError(container, msg) {
  const el = document.createElement('div');
  el.className = 'alert alert-error';
  el.textContent = msg;
  container.prepend(el);
  setTimeout(() => el.remove(), 6000);
}

function showLoading(overlay, text) {
  if (overlay) {
    const textEl = overlay.querySelector('.loading-text');
    if (textEl && text) textEl.textContent = text;
    overlay.classList.add('active');
  }
}

function hideLoading(overlay) {
  if (overlay) overlay.classList.remove('active');
}

function navigateTo(page) {
  window.location.href = '/' + page;
}

function getCharacterInitials(name) {
  if (!name) return '書';
  return name.charAt(0);
}
