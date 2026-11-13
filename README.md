<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jarvis - Voice Interface Integration</title>
<style>
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #1c2128;
  --bg-hover: #21262d;
  --border: #30363d;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --accent: #58a6ff;
  --accent-glow: #58a6ff44;
  --green: #3fb950;
  --green-dim: #238636;
  --yellow: #d29922;
  --red: #f85149;
  --purple: #bc8cff;
  --cyan: #39d353;
  --font-mono: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  --radius: 8px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

/* ─── LAYOUT ─── */
.container {
  max-width: 1080px;
  margin: 0 auto;
  padding: 0 24px;
}

section { padding: 48px 0; }

/* ─── HERO ─── */
.hero {
  text-align: center;
  padding: 80px 0 48px;
  border-bottom: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  pointer-events: none;
  opacity: 0.4;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 100px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 24px;
  font-family: var(--font-mono);
}

.hero-badge .dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.hero h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  letter-spacing: -1px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #e6edf3 0%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero .subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: var(--text-secondary);
  max-width: 640px;
  margin: 0 auto 32px;
}

.hero .subtitle em {
  color: var(--text-muted);
  font-style: normal;
  font-size: 0.9em;
}

/* ─── BADGES ─── */
.badge-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-mono);
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.badge.blue   { border-color: #1f6feb; color: #79c0ff; background: #0c2d6b33; }
.badge.green  { border-color: var(--green-dim); color: #7ee787; background: #23863622; }
.badge.purple { border-color: #6e40c9; color: var(--purple); background: #6e40c922; }
.badge.yellow { border-color: #9e6a03; color: #e3b341; background: #9e6a0322; }
.badge.cyan   { border-color: #1b4721; color: var(--cyan); background: #1b472122; }

/* ─── NAV ─── */
.nav-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}

.nav-links a {
  color: var(--accent);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 14px;
  border-radius: 100px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.nav-links a:hover {
  border-color: var(--border);
  background: var(--bg-secondary);
}

/* ─── TOC ─── */
.toc {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px 28px;
  margin: 32px 0;
}

.toc h3 {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.toc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 4px 24px;
}

.toc-grid a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  padding: 4px 0;
  transition: color 0.2s;
}

.toc-grid a:hover { color: var(--accent); }

/* ─── TYPOGRAPHY ─── */
h2 {
  font-size: clamp(1.4rem, 3vw, 1.9rem);
  font-weight: 700;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  letter-spacing: -0.5px;
}

h3 {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 28px 0 12px;
  color: var(--text-primary);
}

p { margin-bottom: 16px; color: var(--text-secondary); }

a { color: var(--accent); }

strong { color: var(--text-primary); font-weight: 600; }

/* ─── FEATURE CARDS ─── */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 24px 0;
}

.feature-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.25s;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.feature-card:hover {
  border-color: var(--accent);
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(88, 166, 255, 0.1);
}

.feature-card:hover::before { opacity: 1; }

.feature-icon {
  font-size: 28px;
  margin-bottom: 12px;
  display: block;
}

.feature-card h3 {
  margin-top: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.feature-card ul {
  list-style: none;
  padding: 0;
}

.feature-card li {
  padding: 4px 0 4px 20px;
  position: relative;
  font-size: 14px;
  color: var(--text-secondary);
}

.feature-card li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--accent);
}

/* ─── CODE BLOCKS ─── */
.code-block {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin: 16px 0;
  overflow: hidden;
  position: relative;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}

.code-lang {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.code-lang .dot {
  width: 8px; height: 8px;
  border-radius: 50%;
}

.code-lang .dot.red    { background: #ff5f56; }
.code-lang .dot.yellow { background: #ffbd2e; }
.code-lang .dot.green  { background: #27c93f; }

pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-primary);
  tab-size: 2;
}

pre code { font-family: inherit; }

.code-block.terminal pre {
  background: #0a0e14;
  color: #e6edf3;
}

.code-block.terminal .prompt { color: var(--green); }
.code-block.terminal .cmd    { color: var(--text-primary); }
.code-block.terminal .out    { color: var(--text-muted); }
.code-block.terminal .ok     { color: var(--green); }
.code-block.terminal .err    { color: var(--red); }
.code-block.terminal .tts    { color: var(--yellow); }
.code-block.terminal .acc    { color: var(--accent); }

/* ─── TABLES ─── */
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin: 16px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

thead {
  background: var(--bg-secondary);
}

th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

td {
  padding: 11px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  vertical-align: top;
}

tr:last-child td { border-bottom: none; }

tbody tr:hover { background: var(--bg-hover); }

td code, th code {
  font-family: var(--font-mono);
  font-size: 12.5px;
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--accent);
  border: 1px solid var(--border);
}

/* ─── ARCHITECTURE DIAGRAM ─── */
.diagram {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  overflow-x: auto;
  margin: 16px 0;
}

.diagram pre {
  padding: 0;
  font-size: 12.5px;
  color: var(--accent);
  line-height: 1.5;
}

/* ─── PILL / LABEL ─── */
.pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-mono);
}

.pill.success { background: #23863633; color: #7ee787; border: 1px solid var(--green-dim); }
.pill.info    { background: #1f6feb33; color: #79c0ff; border: 1px solid #1f6feb; }
.pill.warning { background: #9e6a0333; color: #e3b341; border: 1px solid #9e6a03; }

/* ─── CHECKLIST ─── */
.checklist {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 8px;
}

.checklist li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.checklist .check {
  color: var(--green);
  font-weight: bold;
  flex-shrink: 0;
}

/* ─── CALLOUT ─── */
.callout {
  border-left: 3px solid var(--accent);
  background: var(--bg-secondary);
  padding: 16px 20px;
  border-radius: 0 var(--radius) var(--radius) 0;
  margin: 16px 0;
}

.callout.warning {
  border-left-color: var(--yellow);
  background: #9e6a0311;
}

.callout .callout-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text-primary);
  font-size: 14px;
}

.callout p:last-child { margin-bottom: 0; }

/* ─── ROADMAP ─── */
.roadmap-section h4 {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  margin: 24px 0 12px;
}

.roadmap-list {
  list-style: none;
  padding: 0;
}

.roadmap-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}

.roadmap-list li:last-child { border-bottom: none; }

.roadmap-list .checkbox {
  width: 16px; height: 16px;
  border: 2px solid var(--border);
  border-radius: 4px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: transparent;
  transition: all 0.2s;
}

.roadmap-list li:hover .checkbox {
  border-color: var(--accent);
  color: var(--accent);
}

/* ─── PROJECT TREE ─── */
.tree {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.8;
  overflow-x: auto;
  color: var(--text-secondary);
}

.tree .dir  { color: var(--accent); font-weight: 600; }
.tree .file { color: var(--text-secondary); }
.tree .cmt  { color: var(--text-muted); }

/* ─── FOOTER ─── */
footer {
  text-align: center;
  padding: 48px 0 64px;
  border-top: 1px solid var(--border);
  margin-top: 48px;
}

footer p {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

footer .heart { color: var(--red); }

/* ─── RESPONSIVE ─── */
@media (max-width: 640px) {
  .container { padding: 0 16px; }
  section { padding: 32px 0; }
  .hero { padding: 48px 0 32px; }
  .toc-grid { grid-template-columns: 1fr; }
  .feature-grid { grid-template-columns: 1fr; }
  pre { font-size: 12px; }
  .diagram pre { font-size: 10.5px; }
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ─── ANCHOR OFFSET ─── */
:target { scroll-margin-top: 24px; }
</style>
</head>
<body>

<div class="container">

<!-- ═══════════════════ HERO ═══════════════════ -->
<header class="hero">
  <div class="hero-badge">
    <span class="dot"></span>
    v2.1.0 · Voice Interface Integration
  </div>

  <h1>🤖 Jarvis</h1>
  <p class="subtitle">
    A cellular calling and dual-SIM balance manager for an AI assistant named Jarvis.<br>
    <em>Powered by an Android companion device for phone calls and USSD-based balance checks.</em>
  </p>

  <div class="badge-row">
    <span class="badge blue">🐍 Python 3.9+</span>
    <span class="badge cyan">🪟 Windows 11 Pro</span>
    <span class="badge green">📱 Android Companion</span>
    <span class="badge purple">🎤 STT + TTS</span>
    <span class="badge yellow">📞 Dual-SIM</span>
    <span class="badge blue">MIT License</span>
  </div>

  <nav class="nav-links">
    <a href="#features">Features</a>
    <a href="#ui">UI Previews</a>
    <a href="#architecture">Architecture</a>
    <a href="#install">Installation</a>
    <a href="#usage">Usage</a>
    <a href="#api">API</a>
    <a href="#security">Security</a>
  </nav>
</header>

<!-- ═══════════════════ OVERVIEW ═══════════════════ -->
<section id="overview">
  <h2>🎯 Overview</h2>
  <p>
    <strong>Jarvis</strong> is an AI assistant that bridges the gap between software and cellular hardware.
    Using an Android companion device as a cellular interface, Jarvis can:
  </p>
  <div class="feature-grid">
    <div class="feature-card">
      <span class="feature-icon">📞</span>
      <h3>Place &amp; Terminate Calls</h3>
      <p>Programmatically dial numbers and end calls via the Android companion device.</p>
    </div>
    <div class="feature-card">
      <span class="feature-icon">💰</span>
      <h3>Dual-SIM Balance</h3>
      <p>Check balances via USSD without initiating voice calls — prefix-based routing.</p>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🎤</span>
      <h3>Voice Commands</h3>
      <p>Process voice commands hands-free with noise reduction and VAD.</p>
    </div>
    <div class="feature-card">
      <span class="feature-icon">🔊</span>
      <h3>Speech Synthesis</h3>
      <p>Respond with synthesized speech for natural, conversational interaction.</p>
    </div>
  </div>
  <div class="callout">
    <div class="callout-title">💡 Why this exists</div>
    <p>Jarvis needed a way to interact with the physical world (calls, balances) and do so hands-free. This repository is that bridge.</p>
  </div>
</section>

<!-- ═══════════════════ TOC ═══════════════════ -->
<section>
  <div class="toc">
    <h3>📋 Table of Contents</h3>
    <div class="toc-grid">
      <a href="#overview">Overview</a>
      <a href="#features">Key Features</a>
      <a href="#ui">UI Previews</a>
      <a href="#architecture">Technical Architecture</a>
      <a href="#pipeline">Voice Pipeline</a>
      <a href="#structure">Project Structure</a>
      <a href="#config">Configuration</a>
      <a href="#install">Installation</a>
      <a href="#usage">Usage Examples</a>
      <a href="#api">REST API</a>
      <a href="#testing">Testing</a>
      <a href="#security">Security</a>
      <a href="#roadmap">Roadmap</a>
      <a href="#support">Support</a>
    </div>
  </div>
</section>

<!-- ═══════════════════ FEATURES ═══════════════════ -->
<section id="features">
  <h2>✨ Key Features</h2>

  <div class="feature-grid">
    <div class="feature-card">
      <span class="feature-icon">📞</span>
      <h3>Cellular Calling</h3>
      <ul>
        <li><strong>Direct dialing</strong> — any phone number via Android companion</li>
        <li><strong>Hang up</strong> — terminate active calls</li>
        <li><strong>Voice interaction</strong> — AI conversation during calls</li>
        <li><strong>Contact management</strong> — resolve names to numbers</li>
        <li><strong>Safety controls</strong> — confirm calls before execution</li>
      </ul>
    </div>

    <div class="feature-card">
      <span class="feature-icon">🎤</span>
      <h3>Voice Interface</h3>
      <ul>
        <li><strong>Speech-to-text</strong> — convert voice to text</li>
        <li><strong>Text-to-speech</strong> — synthesize responses</li>
        <li><strong>Command processing</strong> — recognize &amp; execute</li>
        <li><strong>Multi-language</strong> — process in different languages</li>
        <li><strong>Noise reduction</strong> — enhanced voice quality</li>
      </ul>
    </div>

    <div class="feature-card">
      <span class="feature-icon">💰</span>
      <h3>Dual-SIM Balance Manager</h3>
      <ul>
        <li><strong>Auto-detection</strong> — Ethiopian number prefixes</li>
        <li><code>+2519…</code> / <code>09…</code> → Ethio Telecom (<code>*804#</code>)</li>
        <li><code>+2517…</code> / <code>07…</code> → Safaricom (<code>*704#</code>)</li>
        <li><strong>Manual overrides</strong> — for detection failures</li>
        <li><strong>Smart checking</strong> — no voice call needed</li>
      </ul>
    </div>

    <div class="feature-card">
      <span class="feature-icon">⚙️</span>
      <h3>Configuration &amp; UI</h3>
      <ul>
        <li><strong>Dynamic SIM management</strong> — auto subscription IDs</li>
        <li><strong>Network verification</strong> — via Android APIs</li>
        <li><strong>Auditable operations</strong> — full action logging</li>
        <li><strong>Voice configuration</strong> — custom engine/rate/volume</li>
      </ul>
    </div>
  </div>
</section>

<!-- ═══════════════════ UI PREVIEWS ═══════════════════ -->
<section id="ui">
  <h2>🖥️ UI Previews</h2>

  <h3>1. CLI Interface</h3>
  <div class="code-block terminal">
    <div class="code-header">
      <span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;jarvis_cli.py</span>
      <span>bash</span>
    </div>
    <pre><code><span class="acc">╔══════════════════════════════════════════════════════════════╗
║  🤖  J A R V I S   v2.1   —   Voice Interface Integration     ║
║  Cellular Calling · Dual-SIM Balance · Hands-Free Mode       ║
╚══════════════════════════════════════════════════════════════╝</span>

  <span class="ok">[SIM1]</span> +251954531474  →  Ethio Telecom   (*804#)   Sub ID: 2   <span class="ok">✅</span>
  <span class="ok">[SIM2]</span> +251998065377  →  Ethio Telecom   (*804#)   Sub ID: 5   <span class="ok">✅</span>
  <span class="tts">[MIC ]</span> 🎤 Listening...  Confidence: 0.92   Engine: speech_recognition
  <span class="tts">[TTS ]</span> 🔊 pyttsx3 (rate=150, vol=0.8)                     ACTIVE

  ──────────────────────────────────────────────────────────────
  <span class="prompt">jarvis&gt;</span> <span class="cmd">call 0922233398</span>
  🔊 "Initiating call to 0922233398. Do try to be coherent."
  <span class="ok">✅ Call connected (00:00:03)</span>

  <span class="prompt">jarvis&gt;</span> <span class="cmd">balance --sim SIM1</span>
  🔊 "Checking financial standing on SIM1 (Ethio Telecom). Stand by."
  <span class="ok">✅ Balance: 45.20 ETB | Valid until: 2026-11-30</span>

  <span class="prompt">jarvis&gt;</span> <span class="cmd">status</span>
  <span class="out">  ┌──────────────┬──────────────────────────────────────────┐
  │ Component    │ Status                                   │
  ├──────────────┼──────────────────────────────────────────┤
  │ STT Engine   │ ✅ speech_recognition (en-US)            │
  │ TTS Engine   │ ✅ pyttsx3 (voice_id=0)                  │
  │ SIM1         │ ✅ Ethio Telecom — ready                 │
  │ SIM2         │ ✅ Ethio Telecom — ready                 │
  │ Android Link │ ✅ Connected (USB / ADB)                 │
  └──────────────┴──────────────────────────────────────────┘</span>
  ──────────────────────────────────────────────────────────────
  <span class="out">[Ctrl+C to exit]                         </span><span class="prompt">jarvis&gt;</span></code></pre>
  </div>

  <h3>2. Web Dashboard (Optional)</h3>
  <p>Served at <code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:2px 6px;border-radius:4px;border:1px solid var(--border);font-size:13px;">http://localhost:8000/ui</code> — a lightweight browser UI for non-CLI users.</p>

  <div class="diagram">
<pre>┌────────────────────────────────────────────────────────────────────────┐
│  🤖 JARVIS DASHBOARD                             🟢 Connected   ⚙️     │
├────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────┐   ┌───────────────────────┐                 │
│  │  📞 CALL PANEL        │   │  💰 BALANCE PANEL     │                 │
│  │  ┌─────────────────┐  │   │  SIM1  Ethio Telecom  │                 │
│  │  │ 0922233398      │  │   │  Balance: 45.20 ETB   │                 │
│  │  └─────────────────┘  │   │  [Check]  [Refresh]   │                 │
│  │  [ Dial ]  [ Hangup ] │   │  SIM2  Ethio Telecom  │                 │
│  │  Status: Idle 🟢      │   │  Balance: 12.80 ETB   │                 │
│  └───────────────────────┘   └───────────────────────┘                 │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  🎤 VOICE CONSOLE                                                │ │
│  │  > Check balance for SIM1                      [ 🎤 ] [ ▶️ ]    │ │
│  │  🔊 "Checking balance for SIM1 (Ethio Telecom) using *804#..."  │ │
│  │  ✅ Balance: 45.20 ETB                                          │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘</pre>
  </div>

  <p><strong>Dashboard Features:</strong></p>
  <ul class="checklist">
    <li><span class="check">●</span> Live status indicator (connected / offline)</li>
    <li><span class="check">●</span> Call panel — dial pad, Dial/Hangup, live timer</li>
    <li><span class="check">●</span> Balance panel — per-SIM cards with refresh</li>
    <li><span class="check">●</span> Voice console — mic button, TTS toggle, stream</li>
    <li><span class="check">●</span> Activity log — timestamped audit trail</li>
  </ul>
</section>

<!-- ═══════════════════ ARCHITECTURE ═══════════════════ -->
<section id="architecture">
  <h2>🏗️ Technical Architecture</h2>

  <h3>Components</h3>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>Component</th><th>Path</th><th>Purpose</th></tr>
      </thead>
      <tbody>
        <tr><td>Telephony</td><td><code>core/telephony.py</code></td><td>Cellular communication with Android companion</td></tr>
        <tr><td>USSD Engine</td><td><code>core/ussd.py</code></td><td>USSD balance query execution</td></tr>
        <tr><td>SIM Config</td><td><code>config/ussd_config.json</code></td><td>SIM configuration storage</td></tr>
        <tr><td>Voice Config</td><td><code>config/voice_config.json</code></td><td>Voice settings storage</td></tr>
        <tr><td>CLI</td><td><code>jarvis_cli.py</code></td><td>Unified command-line interface with AI persona</td></tr>
        <tr><td>Voice Interface</td><td><code>voice_interface.py</code></td><td>Speech recognition &amp; synthesis module</td></tr>
        <tr><td>Command Processor</td><td><code>voice_command_processor.py</code></td><td>Advanced voice command processing</td></tr>
        <tr><td>Voice Integration</td><td><code>jarvis_voice_integration.py</code></td><td>Comprehensive voice integration</td></tr>
        <tr><td>Web Dashboard</td><td><code>web/dashboard.html</code></td><td>Browser GUI <em>(optional)</em></td></tr>
        <tr><td>REST API</td><td><code>web/api.py</code></td><td>FastAPI endpoints <em>(optional)</em></td></tr>
      </tbody>
    </table>
  </div>

  <h3>Data Flow</h3>
  <div class="diagram">
<pre>   ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐
   │  🎤 Mic  │──▶ │  Noise Red.  │──▶ │  STT Engine  │──▶ │  Command  │
   └──────────┘    └──────────────┘    └──────────────┘    │  Parser   │
                                                          └─────┬─────┘
                          ┌─────────────────────────────────────┼──────────────┐
                          ▼                                     ▼              ▼
                   ┌─────────────┐                     ┌─────────────┐  ┌───────────┐
                   │  📞 Call    │                     │  💰 Balance │  │  ❓ Help  │
                   └──────┬──────┘                     └──────┬──────┘  └─────┬─────┘
                          │                                   │               │
                          └───────────────┬───────────────────┴───────────────┘
                                          ▼
                                  ┌──────────────┐
                                  │  TTS Engine  │──▶ 🔊 Voice Response
                                  └──────────────┘</pre>
  </div>
</section>

<!-- ═══════════════════ PIPELINE ═══════════════════ -->
<section id="pipeline">
  <h2>🔊 Voice Processing Pipeline</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>#</th><th>Stage</th><th>Description</th></tr>
      </thead>
      <tbody>
        <tr><td>1</td><td><strong>Audio Capture</strong></td><td>Microphone input or audio file</td></tr>
        <tr><td>2</td><td><strong>Preprocessing</strong></td><td>Noise reduction, voice activity detection</td></tr>
        <tr><td>3</td><td><strong>Speech Recognition</strong></td><td>Convert audio to text (STT)</td></tr>
        <tr><td>4</td><td><strong>Command Extraction</strong></td><td>Parse voice command using pattern matching</td></tr>
        <tr><td>5</td><td><strong>Command Validation</strong></td><td>Validate parameters and constraints</td></tr>
        <tr><td>6</td><td><strong>Execution</strong></td><td>Route to appropriate interface (CLI, API, WebSocket)</td></tr>
        <tr><td>7</td><td><strong>Response Generation</strong></td><td>Convert response to speech (TTS)</td></tr>
        <tr><td>8</td><td><strong>Feedback Loop</strong></td><td>Confirm command execution and provide feedback</td></tr>
      </tbody>
    </table>
  </div>
</section>

<!-- ═══════════════════ STRUCTURE ═══════════════════ -->
<section id="structure">
  <h2>📁 Project Structure</h2>
  <div class="tree">
<span class="dir">jarvis-voice-interface/</span>
├── <span class="dir">core/</span>
│   ├── <span class="file">telephony.py</span>              <span class="cmt"># Cellular communication</span>
│   └── <span class="file">ussd.py</span>                   <span class="cmt"># USSD balance query execution</span>
├── <span class="dir">config/</span>
│   ├── <span class="file">ussd_config.json</span>          <span class="cmt"># SIM configuration</span>
│   └── <span class="file">voice_config.json</span>         <span class="cmt"># Voice configuration</span>
├── <span class="dir">voice/</span>
│   ├── <span class="file">voice_interface.py</span>        <span class="cmt"># STT/TTS core</span>
│   ├── <span class="file">voice_command_processor.py</span><span class="cmt"># Command parsing</span>
│   └── <span class="file">jarvis_voice_integration.py</span><span class="cmt"># Full integration</span>
├── <span class="dir">web/</span>
│   ├── <span class="file">dashboard.html</span>            <span class="cmt"># Web dashboard UI</span>
│   └── <span class="file">api.py</span>                    <span class="cmt"># FastAPI endpoints</span>
├── <span class="dir">tests/</span>
│   └── <span class="file">test_ussd_config.py</span>       <span class="cmt"># Unit tests</span>
├── <span class="dir">logs/</span>
│   └── <span class="file">jarvis_audit.log</span>          <span class="cmt"># Audit trail</span>
├── <span class="dir">docs/</span>                         <span class="cmt"># Additional documentation</span>
├── <span class="file">jarvis_cli.py</span>                 <span class="cmt"># CLI entry point</span>
├── <span class="file">requirements.txt</span>
└── <span class="file">README.md</span>
  </div>
</section>

<!-- ═══════════════════ CONFIG ═══════════════════ -->
<section id="config">
  <h2>⚙️ Configuration</h2>

  <h3>Voice Configuration <code style="font-family:var(--font-mono);font-size:0.8em;color:var(--text-muted);">config/voice_config.json</code></h3>
  <div class="code-block">
    <div class="code-header">
      <span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;voice_config.json</span>
      <span>json</span>
    </div>
<pre><code>{
  "voice": {
    "enabled": true,
    "engine": "speech_recognition",
    "language": "en-US",
    "confidence_threshold": 0.85,
    "noise_reduction": true,
    "vad_sensitivity": "medium"
  },
  "commands": {
    "call_keywords": ["call", "dial", "contact"],
    "balance_keywords": ["balance", "credit", "bill"],
    "help_keywords": ["help", "assist", "guide"]
  },
  "tts": {
    "engine": "pyttsx3",
    "voice_id": 0,
    "rate": 150,
    "volume": 0.8
  }
}</code></pre>
  </div>

  <h3>SIM Configuration <code style="font-family:var(--font-mono);font-size:0.8em;color:var(--text-muted);">config/ussd_config.json</code></h3>
  <div class="code-block">
    <div class="code-header">
      <span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;ussd_config.json</span>
      <span>json</span>
    </div>
<pre><code>{
  "sims": {
    "SIM1": {
      "phone_number": "+251954531474",
      "network": null,
      "ussd_code": null,
      "sub_id": 2,
      "manual_override": {
        "network": null,
        "ussd_code": null
      }
    },
    "SIM2": {
      "phone_number": "+251998065377",
      "network": null,
      "ussd_code": null,
      "sub_id": 5,
      "manual_override": {
        "network": null,
        "ussd_code": null
      }
    }
  }
}</code></pre>
  </div>
</section>

<!-- ═══════════════════ INSTALL ═══════════════════ -->
<section id="install">
  <h2>🚀 Installation &amp; Setup</h2>

  <h3>Prerequisites</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Requirement</th><th>Details</th></tr></thead>
      <tbody>
        <tr><td>📱 Android device</td><td>USB debugging enabled</td></tr>
        <tr><td>💻 OS</td><td>Windows 11 Pro (x64)</td></tr>
        <tr><td>🐍 Python</td><td>3.9+</td></tr>
        <tr><td>🎛️ Optional</td><td>Fish Audio API key for enhanced voice</td></tr>
      </tbody>
    </table>
  </div>

  <h3>Setup Steps</h3>

  <p><strong>1. Clone the repository</strong></p>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="prompt">$</span> <span class="cmd">git clone https://github.com/your-org/jarvis-voice-interface.git</span>
<span class="prompt">$</span> <span class="cmd">cd jarvis-voice-interface</span></code></pre>
  </div>

  <p><strong>2. Install dependencies</strong></p>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="prompt">$</span> <span class="cmd">pip install SpeechRecognition pyttsx3 fastapi uvicorn aiohttp</span></code></pre>
  </div>

  <p><strong>3. Configure the Android companion device</strong></p>
  <p>Enable USB debugging and connect via ADB. Confirm with:</p>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="prompt">$</span> <span class="cmd">adb devices</span></code></pre>
  </div>

  <p><strong>4. Configure SIM settings</strong> — Edit <code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:2px 6px;border-radius:4px;border:1px solid var(--border);font-size:13px;">config/ussd_config.json</code> with your SIM details.</p>

  <p><strong>5. Configure voice settings</strong> — Edit <code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:2px 6px;border-radius:4px;border:1px solid var(--border);font-size:13px;">config/voice_config.json</code> with your preferred engine and language.</p>

  <p><strong>6. Launch</strong></p>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="out"># CLI mode</span>
<span class="prompt">$</span> <span class="cmd">python jarvis_cli.py</span>

<span class="out"># Web dashboard + API</span>
<span class="prompt">$</span> <span class="cmd">uvicorn web.api:app --host 0.0.0.0 --port 8000</span>
<span class="out"># → open http://localhost:8000/ui</span></code></pre>
  </div>
</section>

<!-- ═══════════════════ USAGE ═══════════════════ -->
<section id="usage">
  <h2>💡 Usage Examples</h2>

  <h3>🎤 Voice Commands</h3>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Voice Command</th><th>Response</th></tr></thead>
      <tbody>
        <tr><td>"Call 0922233398"</td><td><em>Initiating call to 0922233398. Do try to be coherent.</em></td></tr>
        <tr><td>"Check balance for SIM1"</td><td><em>Checking balance for SIM1 (Ethio Telecom, +251954531474) using *804# (Sub ID: 2)...</em></td></tr>
        <tr><td>"Hang up"</td><td><em>Terminating call. Another riveting conversation cut short.</em></td></tr>
        <tr><td>"Check system status"</td><td><em>Checking system status.</em></td></tr>
        <tr><td>"Help me"</td><td><em>Available voice commands...</em></td></tr>
      </tbody>
    </table>
  </div>

  <h3>🐍 Programmatic Usage</h3>
  <div class="code-block">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;example.py</span><span>python</span></div>
<pre><code>from jarvis_voice_integration import JarvisVoiceIntegration, VoiceIntegrationMode

# Start voice integration
voice = JarvisVoiceIntegration(mode=VoiceIntegrationMode.HYBRID)
voice.start()

# Process voice command
result = voice.process_voice_command(text="Call 0922233398")
print(f"Command result: {result}")

# Get status
status = voice.get_status()
print(f"Voice status: {status}")

# Stop
voice.stop()</code></pre>
  </div>

  <h3>💻 CLI Usage</h3>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="out"># Check SIM 1 balance</span>
<span class="prompt">$</span> <span class="cmd">python jarvis_cli.py balance --sim SIM1</span>
<span class="out">→ Checking financial standing on SIM1 (Ethio Telecom, +251954531474). Stand by.</span>
<span class="out">→ Jarvis: Checking balance for SIM1 (Ethio Telecom, +251954531474) using *804# (Sub ID: 2)...</span>

<span class="out"># Place a call</span>
<span class="prompt">$</span> <span class="cmd">python jarvis_cli.py call --target 0922233398</span>
<span class="out">→ Initiating call to 0922233398. Do try to be coherent.</span>

<span class="out"># Hang up</span>
<span class="prompt">$</span> <span class="cmd">python jarvis_cli.py hangup</span>
<span class="out">→ Terminating call. Another riveting conversation cut short.</span></code></pre>
  </div>
</section>

<!-- ═══════════════════ API ═══════════════════ -->
<section id="api">
  <h2>🌐 REST API Reference</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Example</th></tr>
      </thead>
      <tbody>
        <tr><td><span class="pill success">GET</span></td><td><code>/health</code></td><td>Service health check</td><td><code>curl http://localhost:8000/health</code></td></tr>
        <tr><td><span class="pill success">GET</span></td><td><code>/status</code></td><td>Full system status</td><td><code>curl http://localhost:8000/status</code></td></tr>
        <tr><td><span class="pill success">GET</span></td><td><code>/sims</code></td><td>List SIM details</td><td><code>curl http://localhost:8000/sims</code></td></tr>
        <tr><td><span class="pill info">POST</span></td><td><code>/call</code></td><td>Place a call</td><td><code>curl -X POST -d "target=0922233398"</code></td></tr>
        <tr><td><span class="pill info">POST</span></td><td><code>/hangup</code></td><td>Terminate active call</td><td><code>curl -X POST http://localhost:8000/hangup</code></td></tr>
        <tr><td><span class="pill info">POST</span></td><td><code>/ussd/balance</code></td><td>Check balance for a SIM</td><td><code>curl -X POST -d "sim_id=SIM1"</code></td></tr>
        <tr><td><span class="pill info">POST</span></td><td><code>/voice/command</code></td><td>Process a voice/text command</td><td><code>curl -X POST -d "text=Check balance"</code></td></tr>
      </tbody>
    </table>
  </div>

  <h3>Example Response — <code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:2px 6px;border-radius:4px;border:1px solid var(--border);font-size:13px;">GET /status</code></h3>
  <div class="code-block">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;response.json</span><span>json</span></div>
<pre><code>{
  "status": "ok",
  "voice": {
    "stt_available": true,
    "tts_available": true,
    "engine": "speech_recognition",
    "language": "en-US"
  },
  "sims": {
    "SIM1": { "network": "Ethio Telecom", "ussd_code": "*804#", "sub_id": 2 },
    "SIM2": { "network": "Ethio Telecom", "ussd_code": "*804#", "sub_id": 5 }
  },
  "android_link": "connected",
  "uptime_seconds": 3721
}</code></pre>
  </div>
</section>

<!-- ═══════════════════ TESTING ═══════════════════ -->
<section id="testing">
  <h2>🧪 Testing &amp; Verification</h2>

  <h3>Voice Interface Tests</h3>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="out"># Test voice interface initialization</span>
<span class="prompt">$</span> <span class="cmd">python -c "from voice_interface import JarvisVoiceInterface; \
  voice = JarvisVoiceInterface(); \
  print('Voice interface test:', 'PASSED' if voice.get_status()['stt_available'] else 'FAILED')"</span>

<span class="out"># Test command processor</span>
<span class="prompt">$</span> <span class="cmd">python -c "from voice_command_processor import VoiceCommandProcessor; \
  processor = VoiceCommandProcessor(); \
  cmd = processor.process_voice_input('Call 0922233398', confidence=0.85); \
  print('Command processor test:', 'PASSED' if cmd else 'FAILED')"</span></code></pre>
  </div>

  <h3>Unit Tests</h3>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="out"># Run USSD config unit tests</span>
<span class="prompt">$</span> <span class="cmd">python -m unittest tests/test_ussd_config.py</span>

<span class="out"># Run voice integration tests</span>
<span class="prompt">$</span> <span class="cmd">python -m pytest voice_tests/ -v</span></code></pre>
  </div>

  <h3>✅ Test Results</h3>
  <ul class="checklist">
    <li><span class="check">✅</span> SIM 1 (+251954531474) → Ethio Telecom (*804#)</li>
    <li><span class="check">✅</span> SIM 2 (+251998065377) → Ethio Telecom (*804#)</li>
    <li><span class="check">✅</span> Safaricom prefix (+2517...) → Safaricom Ethiopia (*704#)</li>
    <li><span class="check">✅</span> Manual override functionality</li>
    <li><span class="check">✅</span> Voice interface initialization</li>
    <li><span class="check">✅</span> Command processing and validation</li>
    <li><span class="check">✅</span> Integration with existing systems</li>
  </ul>
</section>

<!-- ═══════════════════ SECURITY ═══════════════════ -->
<section id="security">
  <h2>🔒 Security &amp; Reliability</h2>

  <div class="feature-grid">
    <div class="feature-card">
      <span class="feature-icon">🛡️</span>
      <h3>Voice Security</h3>
      <ul>
        <li><strong>Authentication</strong> — voiceprint (future)</li>
        <li><strong>Authorization</strong> — confirm before execute</li>
        <li><strong>Encryption</strong> — audio &amp; commands</li>
        <li><strong>Audit logging</strong> — all commands logged</li>
        <li><strong>Privacy</strong> — no audio storage by default</li>
      </ul>
    </div>

    <div class="feature-card">
      <span class="feature-icon">🔊</span>
      <h3>Voice Reliability</h3>
      <ul>
        <li><strong>Noise reduction</strong> — advanced cancellation</li>
        <li><strong>VAD</strong> — only process when speaking</li>
        <li><strong>Error recovery</strong> — graceful failure handling</li>
        <li><strong>Fallback</strong> — text input when voice fails</li>
        <li><strong>Monitoring</strong> — real-time metrics</li>
      </ul>
    </div>

    <div class="feature-card">
      <span class="feature-icon">🔐</span>
      <h3>System Security</h3>
      <ul>
        <li><strong>Call confirmation</strong> — explicit user approval</li>
        <li><strong>SIM verification</strong> — via Android APIs</li>
        <li><strong>Input validation</strong> — numbers &amp; USSD codes</li>
        <li><strong>Error handling</strong> — timeouts &amp; failures</li>
        <li><strong>Logging</strong> — all operations auditable</li>
      </ul>
    </div>
  </div>

  <div class="callout warning">
    <div class="callout-title">🐛 USSD Hash Character Fix</div>
    <p><strong>Root Cause:</strong> The <code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:1px 5px;border-radius:4px;border:1px solid var(--border);font-size:13px;">#</code> character was being stripped during USSD command execution due to Android URI handling.</p>
    <p><strong>Solution:</strong> USSD codes are now properly encoded (<code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:1px 5px;border-radius:4px;border:1px solid var(--border);font-size:13px;">*804#</code> → <code style="font-family:var(--font-mono);background:var(--bg-tertiary);padding:1px 5px;border-radius:4px;border:1px solid var(--border);font-size:13px;">*804%23</code>). Android receives and displays complete USSD codes. Comprehensive unit tests verify prefix-based detection and manual overrides.</p>
  </div>

  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;test output</span><span>text</span></div>
<pre><code><span class="ok">Ran 4 tests in 0.002s
OK</span></code></pre>
  </div>
</section>

<!-- ═══════════════════ ROADMAP ═══════════════════ -->
<section id="roadmap" class="roadmap-section">
  <h2>🗺️ Roadmap</h2>

  <h4>🎤 Voice Capabilities</h4>
  <ul class="roadmap-list">
    <li><span class="checkbox">✓</span> Multi-language command processing</li>
    <li><span class="checkbox">✓</span> Voice authentication (speaker verification)</li>
    <li><span class="checkbox">✓</span> Contextual conversation awareness</li>
    <li><span class="checkbox">✓</span> Emotion detection for adaptive responses</li>
    <li><span class="checkbox">✓</span> Personalized command learning</li>
  </ul>

  <h4>🖥️ UI Enhancements</h4>
  <ul class="roadmap-list">
    <li><span class="checkbox">✓</span> Mobile-responsive dashboard</li>
    <li><span class="checkbox">✓</span> Dark/light theme toggle</li>
    <li><span class="checkbox">✓</span> Real-time WebSocket updates</li>
    <li><span class="checkbox">✓</span> Drag-and-drop call queue</li>
    <li><span class="checkbox">✓</span> Voice waveform visualizer</li>
  </ul>

  <h4>🔌 Integration Enhancements</h4>
  <ul class="roadmap-list">
    <li><span class="checkbox">✓</span> WebSocket bidirectional communication</li>
    <li><span class="checkbox">✓</span> Cloud TTS/STT services</li>
    <li><span class="checkbox">✓</span> iOS and native Android apps</li>
    <li><span class="checkbox">✓</span> Smart home device control</li>
    <li><span class="checkbox">✓</span> IoT voice control</li>
  </ul>

  <h4>🚀 Advanced Features</h4>
  <ul class="roadmap-list">
    <li><span class="checkbox">✓</span> Full hands-free operation</li>
    <li><span class="checkbox">✓</span> Background command processing</li>
    <li><span class="checkbox">✓</span> Multi-modal interaction (voice + text + gesture)</li>
    <li><span class="checkbox">✓</span> Adaptive user interface</li>
    <li><span class="checkbox">✓</span> Voice-to-text documentation</li>
  </ul>
</section>

<!-- ═══════════════════ CONTRIBUTING ═══════════════════ -->
<section id="contributing">
  <h2>🤝 Contributing</h2>
  <p>Contributions are welcome! Here's how to get started:</p>
  <div class="code-block terminal">
    <div class="code-header"><span class="code-lang"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span> &nbsp;terminal</span><span>bash</span></div>
<pre><code><span class="out"># 1. Fork the repository</span>
<span class="out"># 2. Create a feature branch</span>
<span class="prompt">$</span> <span class="cmd">git checkout -b feature/amazing-feature</span>

<span class="out"># 3. Commit your changes</span>
<span class="prompt">$</span> <span class="cmd">git commit -m "feat: add amazing feature"</span>

<span class="out"># 4. Push to the branch</span>
<span class="prompt">$</span> <span class="cmd">git push origin feature/amazing-feature</span>

<span class="out"># 5. Open a Pull Request</span></code></pre>
  </div>
  <p>Please ensure:</p>
  <ul class="checklist">
    <li><span class="check">✅</span> All tests pass (<code>python -m unittest discover</code>)</li>
    <li><span class="check">✅</span> Code follows existing style conventions</li>
    <li><span class="check">✅</span> New features include documentation updates</li>
    <li><span class="check">✅</span> Security-sensitive changes are flagged in the PR</li>
  </ul>
</section>

<!-- ═══════════════════ SUPPORT ═══════════════════ -->
<section id="support">
  <h2>📞 Support</h2>
  <p>For technical issues or feature requests related to the voice interface:</p>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Channel</th><th>Link</th></tr></thead>
      <tbody>
        <tr><td>📚 Documentation</td><td>Check the <code>docs/</code> directory</td></tr>
        <tr><td>💬 Community</td><td>Join the Jarvis community for voice feature discussions</td></tr>
        <tr><td>🐛 Issues</td><td><a href="#">Report issues in the repository</a></td></tr>
        <tr><td>✨ Features</td><td><a href="#">Request new voice capabilities</a></td></tr>
      </tbody>
    </table>
  </div>
</section>

<!-- ═══════════════════ FOOTER ═══════════════════ -->
<footer>
  <p><strong>The voice interface provides a comprehensive solution for hands-free operation of Jarvis, enabling users to interact naturally through voice commands while maintaining all existing functionality and security measures.</strong></p>
  <p style="margin-top:16px;">Made with <span class="heart">❤️</span> by the Jarvis Team</p>
  <p style="font-size:12px;color:var(--text-muted);margin-top:8px;">Jarvis v2.1.0 · Voice Interface Integration · MIT License</p>
</footer>

</div>
</body>
</html>
