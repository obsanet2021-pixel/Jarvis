
// ─── Constants ───────────────────────────────────────────────────────────────
const BRIDGE_WS  = 'ws://' + location.hostname + ':8765/ws';
const BRIDGE_API = 'http://' + location.hostname + ':8765';

let ws            = null;
let reconnectTimer = null;
let eventCount     = 0;
let logsBuffer    = [];
let stateSnapshot = {};
let chatHistory   = [];
const VOICE_HISTORY_MAX = 50;

// ─── Navigation ──────────────────────────────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('page-' + btn.dataset.page).classList.add('active');
    if (btn.dataset.page === 'tools') loadTools();
    if (btn.dataset.page === 'permissions') loadPermissions();
    if (btn.dataset.page === 'ai-config') loadAIConfig();
    if (btn.dataset.page === 'voice') fetchVoiceStatus();
    if (btn.dataset.page === 'dashboard') refreshState();
  });
});

// ─── Toasts ──────────────────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.textContent = msg;
  document.getElementById('toasts').appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ─── WebSocket ───────────────────────────────────────────────────────────────
function connectWS() {
  if (ws && ws.readyState <= 1) return;
  setConnStatus('connecting');
  ws = new WebSocket(BRIDGE_WS);

  ws.onopen = () => {
    setConnStatus('online');
    toast('Connected to JARVIS bridge', 'success');
  };

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    handleWSMessage(msg);
  };

  ws.onclose = () => {
    setConnStatus('disconnected');
    reconnectTimer = setTimeout(connectWS, 3000);
  };

  ws.onerror = () => ws.close();
}

function setConnStatus(status) {
  const dot = document.getElementById('conn-dot');
  const txt = document.getElementById('conn-text');
  dot.className = 'dot ' + status;
  txt.textContent = { online: 'Connected', disconnected: 'Disconnected', connecting: 'Connecting…' }[status] || status;
}

function handleWSMessage(msg) {
  if (msg.type === 'snapshot') {
    stateSnapshot = msg.data;
    updateDashboard();
    appendLogs(msg.data.log_buffer || []);
    return;
  }
  if (msg.type === 'connected') {
    document.getElementById('stat-clients').textContent = '1+';
    return;
  }
  if (msg.type === 'event') {
    eventCount++;
    document.getElementById('stat-events').textContent = eventCount;
    const entry = { time: msg.time, tag: msg.tag, msg: formatLogEntry(msg), source: msg.source };
    logsBuffer.push(entry);
    if (logsBuffer.length > 500) logsBuffer = logsBuffer.slice(-500);
    appendLogs([entry]);
    updateDashboard();
    addChatLine('[EVENT] ' + msg.tag + ': ' + JSON.stringify(msg.data), 'system');
  }
  if (msg.type === 'config_updated') {
    toast('Configuration saved', 'success');
  }
  if (msg.type === 'permission_result') {
    toast(msg.approved ? 'Permission approved' : 'Permission denied', msg.approved ? 'success' : 'error');
  }
  // Auto-refresh voice page on relevant events
  if (msg.type === 'event' && ['wake_word.detected', 'speech.starting', 'speech.ended', 'command.transcribed'].includes(msg.tag)) {
    fetchVoiceStatus();
    addVoiceEntry(msg);
  }
}

function addVoiceEntry(msg) {
  const cont = document.getElementById('voice-history');
  if (!cont) return;
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  const tagLabel = {
    'wake_word.detected': '🔔 Wake Word',
    'speech.starting': '🎤 Listening',
    'command.transcribed': '📝 Transcribed',
    'speech.ended': '✅ Ended',
  }[msg.tag] || msg.tag;
  const text = msg.data.wake_word || msg.data.text || msg.data.phrase || '';
  entry.innerHTML = `<span class="log-time">${msg.time}</span> <span>${tagLabel}</span> ${text ? `<span style="color:var(--text-dim)">— "${text}"</span>` : ''}`;
  cont.prepend(entry);
  while (cont.children.length > VOICE_HISTORY_MAX) cont.removeChild(cont.lastChild);
}

function formatLogEntry(evt) {
  const tagClass = { error: 'log-tag-error', permission: 'log-tag-warn', task: 'log-tag-event', agent: 'log-tag-info' }[evt.tag.split('.')[0]] || 'log-tag-info';
  return `<span class="log-time">${evt.time}</span> <span class="log-tag ${tagClass}">[${evt.tag}]</span> <span class="log-msg">${JSON.stringify(evt.data)}</span>`;
}

// ─── Dashboard ───────────────────────────────────────────────────────────────
function updateDashboard() {
  const s = stateSnapshot;
  const stateEl = document.getElementById('stat-state');
  const js = s.jarvis_state || 'UNKNOWN';
  stateEl.textContent = js;
  stateEl.className = 'stat-value ' + ({ IDLE: 'stat-mid', LISTENING: 'stat-up', PROCESSING: 'stat-warn', SPEAKING: 'stat-mid', ERROR: 'stat-down', WAKING: 'stat-up', TASK_COMPLETED: 'stat-up' }[js] || '');

  // Badge
  const badge = document.getElementById('jarvis-state-badge');
  badge.textContent = js;
  badge.className = 'badge ' + ({ IDLE: 'badge-blue', LISTENING: 'badge-green', PROCESSING: 'badge-yellow', SPEAKING: 'badge-blue', ERROR: 'badge-red' }[js] || 'badge-gray');

  // Uptime
  if (s.started_at) {
    const secs = Math.floor(Date.now() / 1000 - s.started_at);
    document.getElementById('stat-uptime').textContent = secs < 60 ? secs + 's' : Math.floor(secs / 60) + 'm';
  }

  // Dashboard log
  const dl = document.getElementById('dash-logs');
  dl.innerHTML = logsBuffer.slice(-20).reverse().map(e => e.html).join('');

  // Hologram state
  updateHologram(js);
}

function refreshState() {
  fetch(BRIDGE_API + '/state')
    .then(r => r.json())
    .then(data => {
      stateSnapshot = data;
      updateDashboard();
    })
    .catch(err => toast('Failed to refresh state: ' + err, 'error'));
}

// ─── Hologram Canvas (simple animated ring) ─────────────────────────────────
const holoCanvas = document.getElementById('holo-canvas');
const holoCtx = holoCanvas.getContext('2d');
let holoPhase = 0;

function drawHologram(state) {
  const ctx = holoCtx;
  const w = holoCanvas.width, h = holoCanvas.height;
  const cx = w / 2, cy = h / 2;
  ctx.clearRect(0, 0, w, h);

  const colors = {
    IDLE: '#3b82f6', LISTENING: '#22c55e', PROCESSING: '#f59e0b',
    SPEAKING: '#06b6d4', WAKING: '#a855f7', TASK_COMPLETED: '#22c55e',
    ERROR: '#ef4444', CALLING: '#f59e0b', HANGING_UP: '#ef4444',
    RINGING: '#f59e0b', IN_CALL: '#22c55e', SHUTDOWN: '#64748b'
  };
  const color = colors[state] || '#64748b';
  const rings  = state === 'PROCESSING' ? 4 : state === 'LISTENING' ? 3 : 2;
  const speed  = state === 'PROCESSING' ? 0.08 : state === 'SPEAKING' ? 0.06 : 0.03;

  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.globalAlpha = 0.6;

  for (let i = 0; i < rings; i++) {
    const r = 20 + i * 12;
    const offset = holoPhase * speed * (i % 2 === 0 ? 1 : -1);
    ctx.beginPath();
    ctx.arc(cx, cy, r, offset, offset + Math.PI * 1.5);
    ctx.stroke();
  }

  // Center dot
  ctx.globalAlpha = 0.9;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(cx, cy, 4, 0, Math.PI * 2);
  ctx.fill();

  holoPhase += 1;
  requestAnimationFrame(() => drawHologram(stateSnapshot.jarvis_state || 'IDLE'));
}
drawHologram('IDLE');

function updateHologram(state) {
  document.getElementById('holo-label').textContent = state + ' — ' + (stateSnapshot.last_message || '');
}

// ─── AI Config ───────────────────────────────────────────────────────────────
async function loadAIConfig() {
  try {
    const r = await fetch(BRIDGE_API + '/config/ai');
    const c = await r.json();
    document.getElementById('cfg-api-key').value = c.api_key_set ? '••••••••' : '';
    document.getElementById('cfg-base-url').value = c.base_url;
    document.getElementById('cfg-model').value = c.model;
  } catch (e) { toast('Failed to load config: ' + e, 'error'); }
}

async function saveAIConfig(testAfter) {
  const payload = {
    api_key:     document.getElementById('cfg-api-key').value,
    base_url:    document.getElementById('cfg-base-url').value,
    model:       document.getElementById('cfg-model').value,
  };
  try {
    const r = await fetch(BRIDGE_API + '/config/ai', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const j = await r.json();
    if (j.status === 'saved') {
      toast('Config saved', 'success');
      if (testAfter) testAIConfig(payload);
    }
  } catch (e) { toast('Save failed: ' + e, 'error'); }
}

async function testAIConfig(payload) {
  const out = document.getElementById('ai-test-result');
  out.innerHTML = '<span style="color:var(--warn)">Testing connection…</span>';
  try {
    const r = await fetch(BRIDGE_API + '/config/ai/test', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const j = await r.json();
    if (j.success) {
      out.innerHTML = `<span style="color:var(--success)">✓ Connection OK — response: "${j.response}"</span>`;
      toast('AI test successful', 'success');
    } else {
      out.innerHTML = `<span style="color:var(--danger)">✗ Test failed: ${j.error || j.response}</span>`;
      toast('AI test failed', 'error');
    }
  } catch (e) {
    out.innerHTML = `<span style="color:var(--danger)">✗ Network error: ${e}</span>`;
  }
}

// ─── Conversation ────────────────────────────────────────────────────────────
function addChatLine(text, role) {
  const cont = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-msg ' + role;
  div.textContent = text;
  cont.appendChild(div);
  cont.scrollTop = cont.scrollHeight;
  chatHistory.push({ role, text });
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addChatLine(text, 'user');

  // Send as simulated voice command through bridge
  try {
    await fetch(BRIDGE_API + '/simulate/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event: 'tool.executed', data: { tool: 'ai_converse', input: text } })
    });
    addChatLine('Message sent to JARVIS backend.', 'system');
  } catch (e) {
    addChatLine('Error sending: ' + e.message, 'system');
  }
}

// ─── Voice ───────────────────────────────────────────────────────────────────
async function fetchVoiceStatus() {
  try {
    const r = await fetch(BRIDGE_API + '/voice/status');
    const d = await r.json();
    document.getElementById('voice-listening').textContent  = d.is_listening  ? 'Yes' : 'No';
    document.getElementById('voice-listening').className   = 'badge ' + (d.is_listening  ? 'badge-green' : 'badge-gray');
    document.getElementById('voice-speaking').textContent  = d.is_speaking   ? 'Yes' : 'No';
    document.getElementById('voice-speaking').className    = 'badge ' + (d.is_speaking   ? 'badge-yellow' : 'badge-gray');
    document.getElementById('voice-wakeword').textContent  = d.wake_word || d.integration_status || '—';
    document.getElementById('voice-wakeword').className    = 'badge ' + (d.integration_status === 'active' ? 'badge-green' : 'badge-blue');

    const log = document.getElementById('voice-log');
    log.textContent = JSON.stringify(d, null, 2);
  } catch (e) { toast('Voice status unavailable: ' + e, 'error'); }
}

// ─── Tools ───────────────────────────────────────────────────────────────────
async function loadTools() {
  try {
    const r = await fetch(BRIDGE_API + '/tools');
    const d = await r.json();
    const cont = document.getElementById('tools-container');
    if (d.error) { cont.innerHTML = `<p style="color:var(--danger);">Error loading tools: ${d.error}</p>`; return; }

    let html = '';
    for (const cat of d.categories || []) {
      html += `<div class="cat-header">${cat}</div><div class="grid-3">`;
      for (const t of (d.tools_by_category[cat] || [])) {
        html += `<div class="tool-card">
          <h4>${esc(t.name)}</h4>
          <p>${esc(t.description)}</p>
          ${t.requires_confirmation ? '<span class="badge badge-yellow">Requires confirmation</span>' : '<span class="badge badge-green">Auto-approved</span>'}
        </div>`;
      }
      html += '</div>';
    }
    cont.innerHTML = html || '<p style="color:var(--text-dim);">No tools registered.</p>';
  } catch (e) { toast('Failed to load tools: ' + e, 'error'); }
}

// ─── Permissions ─────────────────────────────────────────────────────────────
async function loadPermissions() {
  try {
    const r = await fetch(BRIDGE_API + '/permissions');
    const d = await r.json();
    const cont = document.getElementById('perms-container');
    if (d.error) { cont.innerHTML = `<p style="color:var(--danger);">${d.error}</p>`; return; }

    let html = '';
    for (const [name, pol] of Object.entries(d.policies || {})) {
      const levelColor = { READ: 'badge-blue', ROUTINE: 'badge-green', EXTERNAL: 'badge-yellow', CRITICAL: 'badge-red' }[pol.level] || 'badge-gray';
      html += `<div class="perm-row">
        <div class="perm-info">
          <div class="perm-tool">${esc(name)}</div>
          <div class="perm-desc">${esc(pol.description)}</div>
        </div>
        <span class="badge ${levelColor}">${esc(pol.level)}</span>
        <span class="badge ${pol.auto_approve ? 'badge-green' : 'badge-gray'}" style="margin-left:8px;">${pol.auto_approve ? 'Auto' : 'Confirm'}</span>
      </div>`;
    }

    if (d.pending_requests && d.pending_requests.length) {
      html += '<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border);"><strong style="color:var(--warn);">Pending Requests</strong>';
      for (const req of d.pending_requests) {
        html += `<div class="perm-row">
          <div class="perm-info"><div class="perm-tool">${esc(req.tool)}</div><div class="perm-desc">${esc(req.description)}</div></div>
          <div class="perm-actions">
            <button class="btn btn-sm btn-success" onclick="handlePerm('${req.id}',true)">Approve</button>
            <button class="btn btn-sm btn-danger"  onclick="handlePerm('${req.id}',false)">Deny</button>
          </div>
        </div>`;
      }
      html += '</div>';
    }
    cont.innerHTML = html;
  } catch (e) { toast('Failed to load permissions: ' + e, 'error'); }
}

async function handlePerm(id, approve) {
  const url = approve ? `/permissions/${id}/approve` : `/permissions/${id}/deny`;
  await fetch(BRIDGE_API + url, { method: 'POST' });
  loadPermissions();
}

// ─── Logs ────────────────────────────────────────────────────────────────────
function appendLogs(newEntries) {
  const el = document.getElementById('full-logs');
  for (const e of newEntries) {
    const div = document.createElement('div');
    div.className = 'log-entry';
    div.innerHTML = e.html;
    el.appendChild(div);
  }
  el.scrollTop = el.scrollHeight;
}

async function clearLogs() {
  await fetch(BRIDGE_API + '/logs/clear', { method: 'POST' });
  logsBuffer = [];
  document.getElementById('full-logs').innerHTML = '';
  document.getElementById('dash-logs').innerHTML = '';
}

function downloadLogs() {
  const blob = new Blob([logsBuffer.map(e => `[${e.time}] [${e.source}] [${e.tag}] ${JSON.stringify(e.msg)}`).join('\n')], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'jarvis-logs-' + new Date().toISOString().slice(0, 10) + '.txt';
  a.click();
}

// ─── Simulate ────────────────────────────────────────────────────────────────
async function simulateEvent(eventType, data) {
  await fetch(BRIDGE_API + '/simulate/event', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event: eventType, data })
  });
}

// ─── Utility ─────────────────────────────────────────────────────────────────
function esc(s) { return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// ─── Boot ────────────────────────────────────────────────────────────────────
connectWS();
refreshState();
setInterval(() => { document.getElementById('stat-events').textContent = eventCount; }, 10000);
