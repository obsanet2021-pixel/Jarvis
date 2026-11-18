"""
Wake-word activation + live interactive holographic interface for JARVIS.

State machine (12 states, driven by JarvisVoiceIntegration):
    SLEEPING → WAKING → IDLE ↔ LISTENING → PROCESSING → SPEAKING → IDLE
                                      ↘ TASK_COMPLETED → IDLE
    CALLING ↔ RINGING → IN_CALL → HANGING_UP → TASK_COMPLETED → IDLE
    Any state → ERROR → IDLE

Launch with: python jarvis_wake.py
Single-instance lock prevents duplicate windows.
"""

import os
import sys
import subprocess
import threading
import time
import math
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Callable
import argparse

import tkinter as tk
from tkinter import messagebox, ttk


# ---------------------------------------------------------------------------
# Add project root to path so imports work from any launch location
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.jarvis.runtime.event_bus import EventBus, Event, EventType  # noqa: E402
from voice_interface import JarvisVoiceInterface, VoiceCommandResult  # noqa: E402
from core.telephony import AndroidTelephonyAdapter  # noqa: E402

LOGO_FONT = ("Arial", 28, "bold")
STATE_FONT = ("Arial", 14)
META_FONT = ("Consolas", 9)

# ---------------------------------------------------------------------------
# 12-State visual definitions
# ---------------------------------------------------------------------------
class JarvisState(Enum):
    SLEEPING      = "SLEEPING"
    WAKING        = "WAKING"
    IDLE          = "IDLE"
    LISTENING     = "LISTENING"
    PROCESSING    = "PROCESSING"
    SPEAKING      = "SPEAKING"
    CALLING       = "CALLING"
    RINGING       = "RINGING"
    IN_CALL       = "IN_CALL"
    HANGING_UP    = "HANGING_UP"
    TASK_COMPLETED = "TASK_COMPLETED"
    ERROR         = "ERROR"

# Color palette per state
_STATE_COLORS: Dict[JarvisState, str] = {
    JarvisState.SLEEPING:      "#1a1a2e",
    JarvisState.WAKING:        "#00FF7F",   # bright green pulse
    JarvisState.IDLE:          "#4A90D9",   # faint blue
    JarvisState.LISTENING:     "#FFBF00",   # amber
    JarvisState.PROCESSING:    "#00CED1",   # cyan
    JarvisState.SPEAKING:      "#9370DB",   # purple glow
    JarvisState.CALLING:       "#FFA500",   # orange ring
    JarvisState.RINGING:       "#DC143C",   # crimson flash
    JarvisState.IN_CALL:       "#32CD32",   # steady green
    JarvisState.HANGING_UP:    "#DA70D6",   # pale purple fade
    JarvisState.TASK_COMPLETED:"#FFD700",   # gold flash
    JarvisState.ERROR:         "#FF4500",   # red pulsing
}

_WAKE_PHRASES = [
    "hey, jarvis",
    "hello, jarvis",
    "wake up, jarvis",
    "wake up, my boy",
    "son is calling, wake up",
    "what's cooking, jarvis?",
    "what is cooking, jarvis?",
    "hey jarvis",
    "hello jarvis",
    "wake up jarvis",
]


# ---------------------------------------------------------------------------
# HolographicCanvas — pure tkinter rendering engine
# ---------------------------------------------------------------------------
class HolographicCanvas(tk.Canvas):
    """Dark circular HUD widget rendering 12 states via animated canvas primitives."""

    def __init__(self, parent, size: int = 400, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg="#0d0d1a", highlightthickness=0, **kwargs)
        self._size = size
        self._center = size // 2
        self._radius = size // 2 - 16
        self._state: JarvisState = JarvisState.SLEEPING
        self._call_context: str = ""
        self._last_state_change: float = time.time()
        self._anim_phase: float = 0.0  # radians, continuous

        # Draw once immediately
        self._draw()

    # ---- public API -------------------------------------------------------
    def set_state(self, state: JarvisState, context: str = "") -> None:
        if state != self._state:
            self._state = state
            self._last_state_change = time.time()
        if context:
            self._call_context = context
        self.after_idle(self._draw)

    def get_state(self) -> JarvisState:
        return self._state

    # ---- animation loop ---------------------------------------------------
    def _tick(self) -> None:
        self._anim_phase += 0.03  # ~30 rpm equivalent
        self._draw()
        self.after(33, self._tick)  # ~30 fps

    def start_animation(self) -> None:
        self.after(100, self._tick)

    # ---- render ------------------------------------------------------------
    def _draw(self) -> None:
        self.delete("all")
        t = self._anim_phase
        dt = time.time() - self._last_state_change
        st = self._state
        r = self._radius
        cx, cy = self._center, self._center
        col = _STATE_COLORS.get(st, "#FFFFFF")

        # Background fill (subtle radial gradient approximation)
        bg_depth = max(13, min(26, 26 - int(dt * 2) if st in (JarvisState.WAKING, JarvisState.TASK_COMPLETED) else 13))
        self.create_rectangle(0, 0, self._size, self._size, fill=f"#{bg_depth:02x}{bg_depth:02x}{30:02x}", outline="")

        # State-specific layers
        if st == JarvisState.SLEEPING:
            self._draw_sleeping(cx, cy, r, col)
        elif st == JarvisState.WAKING:
            self._draw_waking(cx, cy, r, t)
        elif st == JarvisState.IDLE:
            self._draw_idle(cx, cy, r, t, dt)
        elif st == JarvisState.LISTENING:
            self._draw_listening(cx, cy, r, t, dt)
        elif st == JarvisState.PROCESSING:
            self._draw_processing(cx, cy, r, t, dt)
        elif st == JarvisState.SPEAKING:
            self._draw_speaking(cx, cy, r, t, dt)
        elif st == JarvisState.CALLING:
            self._draw_calling(cx, cy, r, t, dt)
        elif st == JarvisState.RINGING:
            self._draw_ringing(cx, cy, r, t, dt)
        elif st == JarvisState.IN_CALL:
            self._draw_in_call(cx, cy, r, t, dt)
        elif st == JarvisState.HANGING_UP:
            self._draw_hanging_up(cx, cy, r, t, dt)
        elif st == JarvisState.TASK_COMPLETED:
            self._draw_task_completed(cx, cy, r, t, dt)
        elif st == JarvisState.ERROR:
            self._draw_error(cx, cy, r, t, dt)

        # Context label (caller info, etc.)
        if self._call_context:
            self.create_text(cx, cy + r + 14, text=self._call_context,
                             fill="#aaa", font=META_FONT, tags=("ctx",))
            self.tag_raise("ctx")

    # ---- individual state draw methods ------------------------------------

    def _draw_sleeping(self, cx, cy, r, col):
        # Dim sleeping eye — two concentric rings, low opacity feel
        alpha_col = "#0d1b2a"
        for radius in (r, int(r * 0.85), int(r * 0.55)):
            self.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                             outline=alpha_col, width=2 if radius == r else 1)
        # Closed eyelid arc
        self.create_arc(cx - r, cy - r, cx + r, cy + r,
                        start=20, extent=140, style=tk.ARC,
                        outline="#2a3a5a", width=3)

    def _draw_waking(self, cx, cy, r, t):
        # Green pulse expanding outward
        breath = int(4 + 4 * abs(math.sin(t)))
        for i, rad in enumerate((int(r * 0.4), int(r * 0.7), r)):
            alpha = max(0.2, 1.0 - i * 0.3)
            col = f"#{int(0xCC * alpha):02x}{int(0xFF * alpha):02x}{int(0x7F * alpha):02x}"
            w = max(1, breath - i)
            self.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                             outline=col, width=w)
        # Inner diamond
        d = int(r * 0.25)
        self.create_polygon(cx, cy - d, cx + d, cy, cx, cy + d, cx - d, cy,
                            fill="#00FF7F", outline="", stipple="")

    def _draw_idle(self, cx, cy, r, t, dt):
        # Faint blue glow breathing slowly
        breathe = int(1 + 2 * math.sin(t * 0.5))
        for rad in (r, int(r * 0.88)):
            alpha = max(0.35, min(0.8, 0.35 + 0.15 * math.sin(t * 0.5)))
            col = f"#{min(255,int(0x4A * alpha * 3)):02x}{min(255,int(0x90 * alpha * 3)):02x}{min(255,int(0xD9 * alpha * 3)):02x}"
            self.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                             outline=col, width=breathe)
        # Central dot
        self.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#4A90D9", outline="")

    def _draw_listening(self, cx, cy, r, t, dt):
        # Amber radial fill that rotates
        segments = 12
        seg_angle = 360 / segments
        for i in range(segments):
            angle = int(seg_angle * i + t * 30) % 360
            end = int(angle + seg_angle * 0.8)
            x0 = cx + r * math.cos(math.radians(angle - 90))
            y0 = cy + r * math.sin(math.radians(angle - 90))
            x1 = cx + r * math.cos(math.radians(end - 90))
            y1 = cy + r * math.sin(math.radians(end - 90))
            fill_col = f"#FF{int(0xBF * (0.5 + 0.5 * math.sin(t + i))):02x}00"
            self.create_polygon(cx, cy, x0, y0, x1, y1, fill=fill_col, outline="")
        # Ring border
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline="#FFBF00", width=2)
        # Center mic icon (circle + line)
        self.create_oval(cx - 10, cy - 14, cx + 10, cy + 2,
                         outline="#FFBF00", width=2)
        self.create_arc(cx - 6, cy + 2, cx + 6, cy + 12,
                        start=180, extent=180, style=tk.ARC, outline="#FFBF00", width=2)

    def _draw_processing(self, cx, cy, r, t, dt):
        # Spinning arcs (cyan)
        arc_len = 60
        n_arcs = 3
        for i in range(n_arcs):
            base = int(t * 60 + i * (360 // n_arcs))
            self.create_arc(cx - r, cy - r, cx + r, cy + r,
                            start=base, extent=arc_len,
                            style=tk.ARC, outline="#00CED1", width=3)
        # Pulsing center
        pulse = int(6 + 4 * abs(math.sin(t * 3)))
        self.create_oval(cx - pulse, cy - pulse, cx + pulse, cy + pulse,
                         outline="#00CED1", width=2)
        # Radial lines
        for i in range(6):
            angle = int(i * 60 + t * 20)
            rad = int(r * 0.55)
            x1 = cx + rad * math.cos(math.radians(angle - 90))
            y1 = cy + rad * math.sin(math.radians(angle - 90))
            x2 = cx + rad * 0.35 * math.cos(math.radians(angle - 90))
            y2 = cy + rad * 0.35 * math.sin(math.radians(angle - 90))
            self.create_line(x1, y1, x2, y2, fill="#00CED1", width=1)

    def _draw_speaking(self, cx, cy, r, t, dt):
        # Audio wave bars
        bar_count = 24
        bar_w = (r * 2) // bar_count
        for i in range(bar_count):
            h = int(10 + 25 * abs(math.sin(t * 4 + i * 0.5)))
            x = cx - r + i * bar_w + 2
            col = f"#{int(0x93 + 0x20 * math.sin(t + i)):02x}" \
                  f"{int(0x70 + 0x20 * math.sin(t + i + 1)):02x}" \
                  f"{int(0xDB + 0x20 * math.sin(t + i + 2)):02x}"
            self.create_rectangle(x, cy - h // 2, x + bar_w - 4, cy + h // 2,
                                  fill=col, outline="")
        # Border
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline="#9370DB", width=2)

    def _draw_calling(self, cx, cy, r, t, dt):
        # Orange concentric rings radiating outward
        for i in range(3):
            phase = ((t * 30 + i * 40) % 120) / 120
            rad = int(r * (0.3 + 0.7 * phase))
            alpha = max(0, 1 - phase)
            col = f"#{int(0xFF * alpha):02x}{int(0xA5 * alpha):02x}00"
            self.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                             outline=col, width=2)
        # Phone icon
        self.create_text(cx, cy, text="📞", font=("Segoe UI Emoji", 24),
                         fill="#FFA500")

    def _draw_ringing(self, cx, cy, r, t, dt):
        # Flashing red
        flash = int(0.5 + 0.5 * math.sin(t * 8))
        col = f"#{int(0xDC * flash):02x}14{int(0x3C * flash):02x}"
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=col, width=4)
        self.create_oval(cx - r * 0.75, cy - r * 0.75, cx + r * 0.75, cy + r * 0.75,
                         outline=col, width=2)
        for i in range(8):
            angle = i * 45 + t * 60
            rad = int(r * 0.9)
            x = cx + rad * math.cos(math.radians(angle - 90))
            y = cy + rad * math.sin(math.radians(angle - 90))
            self.create_oval(x - 4, y - 4, x + 4, y + 4,
                             fill=col, outline="")
        self.create_text(cx, cy, text="RING", font=("Arial", 14, "bold"),
                         fill=col)

    def _draw_in_call(self, cx, cy, r, t, dt):
        # Steady green — outer ring solid, inner pulsing
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline="#32CD32", width=3)
        pulse = int(8 + 3 * math.sin(t * 2))
        self.create_oval(cx - pulse * 3, cy - pulse * 3,
                         cx + pulse * 3, cy + pulse * 3,
                         outline="#32CD32", width=2)
        # Timer-like arc
        elapsed = int(dt)
        mins, secs = divmod(elapsed, 60)
        self.create_text(cx, cy, text=f"{mins:02d}:{secs:02d}",
                         font=("Consolas", 16), fill="#32CD32")

    def _draw_hanging_up(self, cx, cy, r, t, dt):
        # Purple fade — fading rings
        fade = max(0, 1 - dt / 3.0)
        for i in range(3):
            rad = int(r * (0.4 + i * 0.25) * (0.5 + 0.5 * fade))
            col = f"#{int(0xDA * fade):02x}{int(0x70 * fade):02x}{int(0xD6 * fade):02x}"
            self.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                             outline=col, width=2)
        self.create_text(cx, cy, text="↑", font=("Arial", 20, "bold"),
                         fill=f"#{int(0xDA * fade):02x}{int(0x70 * fade):02x}{int(0xD6 * fade):02x}")

    def _draw_task_completed(self, cx, cy, r, t, dt):
        # Gold flash → fades back
        flash = max(0, 1 - dt / 1.5)
        col = f"#{min(255,int(0xFF*flash+32)):02x}{min(255,int(0xD7*flash+32)):02x}{min(255,int(0x00*flash+32)):02x}"
        # Burst rays
        for i in range(12):
            angle = i * 30 + t * 40
            rad_inner = int(r * 0.3)
            rad_outer = int(r * (0.6 + 0.4 * flash))
            x1 = cx + rad_inner * math.cos(math.radians(angle - 90))
            y1 = cy + rad_inner * math.sin(math.radians(angle - 90))
            x2 = cx + rad_outer * math.cos(math.radians(angle - 90))
            y2 = cy + rad_outer * math.sin(math.radians(angle - 90))
            self.create_line(x1, y1, x2, y2, fill=col, width=2)
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=col, width=max(1, int(3 * flash)))
        self.create_text(cx, cy, text="✓", font=("Arial", 28, "bold"),
                         fill=col)

    def _draw_error(self, cx, cy, r, t, dt):
        # Red pulsing X
        pulse = int(0.5 + 0.5 * math.sin(t * 5))
        col = f"#{int(0xFF * pulse + 0x45):02x}{int(0x45 * pulse + 0x20):02x}00"
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=col, width=3)
        diag = int(r * 0.5)
        self.create_line(cx - diag, cy - diag, cx + diag, cy + diag,
                         fill=col, width=3)
        self.create_line(cx + diag, cy - diag, cx - diag, cy + diag,
                         fill=col, width=3)


# ---------------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------------
class JarvisWakeApp:
    """Single-window app: holographic canvas + status bar + log."""

    WIDTH, HEIGHT = 520, 700

    def __init__(self, root: tk.Tk, event_bus: EventBus,
                 voice_iface: JarvisVoiceInterface,
                 telephony: AndroidTelephonyAdapter):
        self.root = root
        self.bus = event_bus
        self.voice = voice_iface
        self.tele = telephony
        self._current_jarvis_state: JarvisState = JarvisState.SLEEPING
        self._lock = threading.Lock()
        # Post-wake "listening window" flag — suppresses re-matching wake phrases
        # within 8 s of a wake acknowledgment so the command portion isn't eaten.
        self._in_conversation = False
        self._ai_client = None  # set lazily on first non-hardware query

        # Build window
        self.root.title("JARVIS — Wake Mode")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.minsize(self.WIDTH, self.HEIGHT)
        self.root.configure(bg="#0d0d1a")

        self._build_ui()
        self._subscribe_events()

        # Subscribe to voice result callback — drives state transitions
        self.voice.register_callback('voice_result', self._on_voice_result)

        # Clap acoustic detector
        self._clap = _ClapDetector()
        self._clap.on_clap(self._on_clap_detected)
        self._audio_thread: Optional[threading.Thread] = None
        self._audio_stream = None
        self._start_clap_listener()

        # Publish startup
        self._transition(JarvisState.SLEEPING)
        self.bus.publish_simple(EventType.STARTUP, source="jarvis_wake")

    def _start_clap_listener(self) -> None:
        """Start a background PyAudio stream feeding the clap detector."""
        try:
            import pyaudio
        except Exception as e:
            self._log(f"[clap] PyAudio unavailable: {e}")
            return

        try:
            pa = pyaudio.PyAudio()
            # Prefer Mic Array (device 4) if present; fall back to default input.
            default_info = pa.get_default_input_device_info()
            device_idx = int(default_info.get("index", 0))
            sr = int(default_info.get("defaultSampleRate", 44100))
            self._audio_stream = pa.open(
                format=pyaudio.paInt16, channels=1, rate=sr,
                input=True, frames_per_buffer=self._ClapDetector.CHUNK,
                input_device_index=device_idx,
            )
            self._audio_thread = threading.Thread(
                target=self._audio_loop, daemon=True, name="clap-listener"
            )
            self._audio_thread.start()
            self._log(f"[clap] Listening on mic #{device_idx} ({sr} Hz)")
        except Exception as e:
            self._log(f"[clap] Failed to open mic: {e}")

    def _audio_loop(self) -> None:
        chunk = _ClapDetector.CHUNK
        try:
            while self._audio_stream and not self._audio_stream.is_closed():
                frame = self._audio_stream.read(chunk, exception_on_overflow=False)
                self._clap.process_frame(frame)
        except Exception as e:
            self._log(f"[clap] Stream error: {e}")

    def _on_clap_detected(self) -> None:
        """Fire on main thread to keep state mutations serialised."""
        self.root.after(0, self._handle_clap)

    def _handle_clap(self) -> None:
        # If already in conversation, treat as wake so user can start fresh.
        with self._lock:
            in_conv = self._in_conversation
        if in_conv:
            self._log("[clap] Clap during conversation — re-waking")
        self._log("[clap] CLAP detected!")
        self._transition(JarvisState.WAKING)
        self._speak("Hey! I'm up.")
        self.root.after(800, lambda: self._transition(JarvisState.IDLE))
        self.root.after(1500, self._start_conversation_window)

    # ---- UI construction --------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 6}
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main, text="⟨ J A R V I S ⟩",
                          font=("Arial", 18, "bold"), foreground="#4A90D9")
        title.pack(**pad)

        # Holographic canvas
        self.holo = HolographicCanvas(main, size=360)
        self.holo.pack(pady=(0, 8))

        # Status frame
        sf = ttk.LabelFrame(main, text="System Status", padding=8)
        sf.pack(fill=tk.X, padx=8)

        self.status_label = ttk.Label(sf, text="State: SLEEPING",
                                       font=("Arial", 12, "bold"), foreground="#aaa")
        self.status_label.pack(anchor="w")
        self.context_label = ttk.Label(sf, text="Context: —",
                                        font=META_FONT, foreground="#777")
        self.context_label.pack(anchor="w")

        # Log
        logf = ttk.LabelFrame(main, text="Event Log", padding=8)
        logf.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 0))

        self.log_txt = tk.Text(logf, height=8, font=META_FONT,
                               bg="#1a1a2e", fg="#c8ffc8", relief="flat",
                               insertbackground="#c8ffc8", wrap="word")
        lsbar = ttk.Scrollbar(logf, orient=tk.VERTICAL, command=self.log_txt.yview)
        self.log_txt.configure(yscrollcommand=lsbar.set)
        self.log_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lsbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom buttons
        btnf = ttk.Frame(main)
        btnf.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(btnf, text="Exit", command=self._exit).pack(side=tk.RIGHT)
        ttk.Button(btnf, text="Test Wake Word",
                   command=lambda: self._simulate_wake()).pack(side=tk.RIGHT, padx=(0, 8))

        self._log("JARVIS wake-mode initialized.")

    # ---- EventBus subscription --------------------------------------------

    def _subscribe_events(self) -> None:
        for evt_type in (EventType.TASK_COMPLETED, EventType.ERROR,
                         EventType.PERMISSION_GRANTED, EventType.PERMISSION_DENIED):
            self.bus.subscribe(evt_type, self._on_event)

    def _on_event(self, event: Event) -> None:
        self.root.after(0, self._handle_event, event)

    def _handle_event(self, event: Event) -> None:
        tag = event.type.value
        data = event.data
        src = event.source
        if tag == "task.completed":
            self._transition(JarvisState.TASK_COMPLETED, context=data.get("task", ""))
            self._speak("Task completed.")
            self._log(f"[{tag}] {data}")
        elif tag == "error":
            self._transition(JarvisState.ERROR, context=data.get("message", "Error"))
            self._log(f"[{tag}] {data}")
        elif tag in ("permission.granted", "permission.denied"):
            self._log(f"[{tag}] {data}")

    # ---- Voice result handler (drives wake-word → command flow) -----------

    def _on_voice_result(self, result: VoiceCommandResult) -> None:
        """Called on voice thread; must marshal to main thread."""
        text_lower = result.text.lower().strip()
        self.root.after(0, self._handle_voice_result, result, text_lower)

    def _handle_voice_result(self, result: VoiceCommandResult, raw: str) -> None:
        # During a conversation window, wake phrases are ignored — the mic may
        # pick up the TTS acknowledgment or room ambience as a false trigger.
        if self._in_conversation:
            self._log(f"CONVERSATION LISTEN: '{raw}'")
            self._process_command(result, raw)
            return

        detected_phrase = self._match_wake_phrase(raw)
        if detected_phrase:
            self._log(f"WAKE WORD detected: '{detected_phrase}'")
            self._transition(JarvisState.WAKING)
            # Extract any command text that followed the wake phrase (e.g.
            # "hey jarvis what time is it" → remaining "what time is it").
            prefix = detected_phrase.split(",")[0]  # e.g. "hey"
            rest_of_utterance = ""
            t = raw.lower().strip().replace("'", "").replace(",", "")
            idx = t.find(prefix)
            if idx >= 0:
                rest_of_utterance = raw[idx + len(prefix):].strip(" ,:.!?;\"'")
            ack = f"Hey! I'm ready."
            self._speak(ack)
            self._log(f"WAKE ACKNOWLEDGED: '{ack}'")
            # Hold in WAKING state briefly for visual effect, then LISTENING.
            self.root.after(800, lambda: self._transition(JarvisState.IDLE))
            self.root.after(1500, self._start_conversation_window)
            # If there was a command attached to the wake utterance, process it now.
            if rest_of_utterance:
                self._log(f"WAKE COMMAND DIRECT: '{rest_of_utterance}'")
                from voice_interface import VoiceCommandResult as _VCR, VoiceCommand as _VC
                self._process_command(_VCR(command=_VC.UNKNOWN, confidence=0.9, text=rest_of_utterance, parameters={}), rest_of_utterance)
            return

        # No wake word matched — treat as direct command if listening/idle.
        with self._lock:
            cur = self._current_jarvis_state
        if cur in (JarvisState.IDLE, JarvisState.LISTENING):
            self._log(f"COMMAND RECOGNIZED: '{raw}'")
            self._process_command(result, raw)

    def _start_conversation_window(self) -> None:
        """Transition to LISTENING and flag that we're in an active conversation."""
        with self._lock:
            self._in_conversation = True
        self._transition(JarvisState.LISTENING)
        # Auto-close the conversation window after 12 seconds of silence.
        self.root.after(12000, self._close_conversation_window)

    def _close_conversation_window(self) -> None:
        with self._lock:
            self._in_conversation = False
        self._transition(JarvisState.IDLE)

    def _match_wake_phrase(self, text: str) -> Optional[str]:
        """Return matched wake phrase string or None."""
        t = text.lower().strip().replace("'", "").replace(",", "")
        for phrase in _WAKE_PHRASES:
            # Normalise comparison phrase to the same form as input text
            p = phrase.replace("'", "").replace(",", "").strip()
            if t == p:
                return phrase
            # Only match by prefix when the input starts with the full first token
            # (e.g. "hello, jarvis" splits into ["hello", "jarvis"]; "hello j..."
            # could still be "hello my friend" so we require the first *two* tokens
            # to start with to avoid false positives on single-word prefixes).
            parts = p.split()
            if len(parts) >= 2:
                # Require at least the first two meaningful words as prefix
                if t.startswith(" ".join(parts[:2])):
                    return phrase
            elif len(parts) == 1 and t.startswith(parts[0]):
                # Single-word prefixes only match exact or well-formed utterances
                # Guard against very common one-word starters by requiring ≥3 chars
                if len(parts[0]) > 2 and len(t) >= len(parts[0]) + 1:
                    return phrase
        return None

    def _process_command(self, result: VoiceCommandResult, raw: str) -> None:
        cmd = result.command.value
        self._log(f"PROCESSING CMD: {cmd} | '{raw}'")
        if cmd == "call":
            target = result.parameters.get("target", "")
            if not target:
                self._speak("Please provide a phone number.")
                self._transition(JarvisState.IDLE)
                return
            self._transition(JarvisState.CALLING, context=f"Calling {target}")
            self._speak(f"Calling {target}.")
            self.bus.publish_simple(EventType.TASK_COMPLETED,
                                    data={"task": f"call:{target}"})
        elif cmd == "balance":
            sim = result.parameters.get("sim", "SIM1")
            self._transition(JarvisState.PROCESSING, context=f"Checking {sim} balance")
            self._speak(f"Checking {sim} balance.")
            self.bus.publish_simple(EventType.TASK_COMPLETED,
                                    data={"task": f"balance:{sim}"})
        elif cmd == "hangup":
            self._transition(JarvisState.HANGING_UP, context="Ending call")
            self._speak("Ending call.")
            self.bus.publish_simple(EventType.TASK_COMPLETED, data={"task": "hangup"})
        elif cmd == "status":
            self._transition(JarvisState.PROCESSING, context="Checking status")
            self._speak("Checking system status.")
            self.bus.publish_simple(EventType.TASK_COMPLETED, data={"task": "status"})
        elif cmd == "help":
            self._speak("Available commands: call, balance, hangup, status. Or ask me anything else.")
        elif cmd == "exit":
            self._speak("Goodbye.")
            self.root.after(500, self.root.quit)
        else:
            # Unknown/hardware command — fall back to AI backend.
            self._ai_converse(raw)

    def _get_ai_client(self):
        """Lazily initialise an OpenAI-compatible LLM client via FreeLLMAPI."""
        if self._ai_client is not None:
            return self._ai_client
        try:
            from openai import OpenAI
            api_key = os.getenv("FREELLMAPI_API_KEY")
            base_url = os.getenv("FREELLMAPI_BASE_URL", "https://api.freellmapi.com/v1")
            model = os.getenv("FREELLMAPI_MODEL", "kokoro")
            if not api_key:
                self._log("[AI] FREELLMAPI_API_KEY not set — AI replies disabled")
                return None
            self._ai_client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=30.0,
            )
            self._log(f"[AI] Client initialised (model={model}, url=<masked>)")
        except Exception as e:
            self._log(f"[AI] Failed to init: {e}")
            return None

    def _ai_converse(self, user_text: str) -> None:
        """Send user text to AI backend and speak the response."""
        self._log(f"AI PROCESSING: '{user_text}'")
        self._transition(JarvisState.PROCESSING, context="Consulting AI")
        client = self._get_ai_client()
        if client is None:
            self._speak("I don't have an AI backend configured right now.")
            self.root.after(1500, lambda: self._transition(JarvisState.IDLE))
            return
        try:
            from src.jarvis.agent.model_adapter import ModelConfig, ModelAdapter
            mc = ModelConfig(provider="openai", model=os.getenv("FREELLMAPI_MODEL", "kokoro"),
                             api_key=os.getenv("FREELLMAPI_API_KEY", ""),
                             base_url=os.getenv("FREELLMAPI_BASE_URL", "https://api.freellmapi.com/v1"))
            adapter = ModelAdapter(mc)
            adapter.initialize()
            reply = adapter.generate([
                {"role": "system", "content": "You are JARVIS, a helpful assistant. Keep responses concise and under two sentences unless asked for detail."},
                {"role": "user", "content": user_text},
            ])
            content = (reply.get("content") or "").strip()
            if not content:
                err = reply.get("error", "empty response")
                self._log(f"[AI] Empty reply — error: {err}")
                self._speak("I couldn't get a response from my brain. Try again.")
            else:
                self._log(f"AI RESPONSE: '{content[:120]}'")
                self._speak(content)
        except Exception as e:
            self._log(f"[AI] Error: {e}")
            self._speak("Sorry, I ran into an issue processing that.")
        finally:
            self.root.after(2000, lambda: self._transition(JarvisState.IDLE))

    # ---- State machine ----------------------------------------------------

    def _transition(self, state: JarvisState, context: str = "") -> None:
        with self._lock:
            self._current_jarvis_state = state
        color = _STATE_COLORS[state]
        self.holo.set_state(state, context)
        self.status_label.config(text=f"State: {state.value}", foreground=color)
        self.context_label.config(text=f"Context: {context or '—'}")
        self._log(f"→ {state.value}" + (f" [{context}]" if context else ""))

    # ---- TTS wrapper ------------------------------------------------------

    def _speak(self, text: str) -> None:
        """Speak on main thread (TTS runs on its own thread internally)."""
        self.root.after(0, self._do_speak, text)

    def _do_speak(self, text: str) -> None:
        self._transition(JarvisState.SPEAKING)
        # Pause mic-listening while speaking to prevent echo/capture of our own output.
        was_listening = self.voice.is_listening
        if was_listening:
            self.voice.stop_listening()
        self.voice.speak(text)
        # Resume listening once speech finishes (~1.5 s for short utterances, longer for extended).
        duration_ms = max(1500, int(len(text) * 60))
        self.root.after(duration_ms, lambda: self._resume_listening(was_listening))

    def _resume_listening(self, was_listening: bool) -> None:
        if was_listening:
            self.voice.start_listening(callback=self._on_voice_result)

    # ---- Helpers ----------------------------------------------------------

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_txt.config(state=tk.NORMAL)
        self.log_txt.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_txt.see(tk.END)
        self.log_txt.config(state=tk.DISABLED)

    def _simulate_wake(self) -> None:
        """Press button to simulate a wake-word detection for testing."""
        from voice_interface import VoiceCommandResult, VoiceCommand
        result = VoiceCommandResult(
            command=VoiceCommand.UNKNOWN,
            confidence=1.0,
            text="Hey JARVIS",
            parameters={}
        )
        self._on_voice_result(result)

    def _exit(self) -> None:
        if messagebox.askyesno("Exit", "Shut down JARVIS?"):
            self.voice.stop_listening()
            try:
                if self._audio_stream and not self._audio_stream.is_closed():
                    self._audio_stream.close()
            except Exception:
                pass
            self.bus.publish_simple(EventType.SHUTDOWN, source="jarvis_wake")
            self.root.destroy()


# ---------------------------------------------------------------------------
# Single-instance lock
# ---------------------------------------------------------------------------
def acquire_lock(lock_path: Path) -> Optional[Path]:
    """Try to create an exclusive lock file. Returns path on success, None on failure.

    Stale locks (PID no longer running) are cleaned up automatically.
    """
    if lock_path.exists():
        try:
            pid_text = lock_path.read_text().strip()
            pid = int(pid_text)
        except (ValueError, UnicodeDecodeError):
            # Corrupt lock — treat as stale
            pass
        else:
            # Check if process is alive. os.kill(pid, 0) raises OSError on both
            # POSIX and Windows when the target PID does not exist.
            import ctypes, signal
            alive = False
            try:
                if sys.platform == "win32":
                    handle = ctypes.windll.kernel32.OpenProcess(
                        0x0410, False, pid  # PROCESS_QUERY_LIMITED_INFORMATION
                    )
                    alive = handle != 0
                    if alive:
                        ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    os.kill(pid, signal.SIG_DFL)
                    alive = True
            except OSError:
                pass
            if alive:
                return None
            # Dead PID — remove stale lock so we can claim it.
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return lock_path
    except FileExistsError:
        return None


def release_lock(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS wake-word assistant")
    parser.add_argument("--no-gui", action="store_true", help="Run in headless mode (web bridge only)")
    args = parser.parse_args()

    lock_file = Path.home() / ".jarvis_wake.lock"
    if acquire_lock(lock_file) is None:
        print("[jarvis_wake] Another instance is already running.")
        return 1

    # Verify STT & TTS availability
    from voice_interface import STT_AVAILABLE, TTS_AVAILABLE
    if not TTS_AVAILABLE:
        print("[jarvis_wake] pyttsx3 not available — TTS disabled.")
    if not STT_AVAILABLE:
        print("[jarvis_wake] WARNING: SpeechRecognition not available — "
              "wake-word listening will be non-functional.")

    bus = EventBus()
    voice = JarvisVoiceInterface()

    # ADB/telephony setup — reuse the same convention as api/main.py
    adb_candidate = Path("platform-tools/platform-tools/adb.exe")
    adb_path = str(adb_candidate.resolve()) if adb_candidate.exists() else "adb"
    device_id = os.environ.get("JARVIS_DEVICE_ID", "")
    if not device_id:
        try:
            result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, timeout=10, check=False)
            for line in result.stdout.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    device_id = parts[0]
                    break
        except Exception:
            pass
    tele = AndroidTelephonyAdapter(adb_path, device_id)

    # ── Headless path: bridge + keepalive, no GUI ───────────────────────────
    if args.no_gui:
        print("[jarvis_wake] Running in --no-gui mode (headless)")

        # Start the web bridge on a background thread
        import threading as _threading
        try:
            from bridge.websocket_bridge import start_bridge_sync
            t = _threading.Thread(target=start_bridge_sync, args=(bus, 8765), daemon=True)
            t.start()
            print("[jarvis_wake] Web bridge listening on ws://127.0.0.1:8765/ws")
            print("[jarvis_wake] Open http://127.0.0.1:8765 in your browser for the JARVIS dashboard.")
        except Exception as _berr:
            print(f"[jarvis_wake] Web bridge failed to start: {_berr}")

        def _on_close():
            voice.stop_listening()
            release_lock(lock_file)
            bus.publish_simple(EventType.SHUTDOWN, source="jarvis_wake")

        # Register SIGINT/SIGTERM cleanup
        import signal
        def _sig_handler(signum, frame):
            _on_close()
            raise SystemExit(0)
        signal.signal(signal.SIGINT, _sig_handler)
        signal.signal(signal.SIGTERM, _sig_handler)

        while True:
            time.sleep(60)
        return 0  # unreachable but keeps linters happy

    # ── GUI path ─────────────────────────────────────────────────────────────
    root = tk.Tk()
    app = JarvisWakeApp(root, bus, voice, tele)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
