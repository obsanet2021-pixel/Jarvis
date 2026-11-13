"""
Enhanced GUI for Jarvis with Holographic Interface

This module provides an enhanced GUI for Jarvis that integrates the holographic
interface with the existing Windows desktop application. It combines the
3D holographic character display with all of Jarvis's functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from holographic_interface import HologramRenderer3D, HologramState
from jarvis_voice_integration import JarvisVoiceIntegration, VoiceIntegrationMode

class EnhancedJarvisGUI:
    """Enhanced GUI with holographic interface for Jarvis"""

    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS - Enhanced GUI with Holographic Interface")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Initialize components
        self.holographic_renderer = None
        self.voice_integration = None
        self.is_holographic_active = False

        # State management
        self.current_hologram_state = HologramState(
            id="main_hologram",
            name="Jarvis Hologram",
            state="IDLE",
            position={"x": 0, "y": 0, "z": 0},
            rotation={"x": 0, "y": 0, "z": 0},
            scale=1.0,
            color="#00ffff",
            glow_intensity=0.5,
            animation="idle",
            confidence=0.9
        )

        # GUI components
        self.create_interface()
        self.setup_holographic_renderer()
        self.setup_voice_integration()

    def create_interface(self):
        """Create the GUI interface"""
        # Main layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Title bar
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(
            title_frame,
            text="JARVIS - Holographic Interface Enhanced",
            font=("Arial", 18, "bold"),
            foreground="#00ffff"
        )
        title_label.pack(side=tk.LEFT)

        # Holographic status indicator
        self.holographic_status_label = ttk.Label(
            title_frame,
            text="Holographic: INACTIVE",
            font=("Arial", 10),
            foreground="red"
        )
        self.holographic_status_label.pack(side=tk.RIGHT)

        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Holographic display area
        holographic_frame = ttk.LabelFrame(content_frame, text="Holographic Display", padding="10")
        holographic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Create placeholder for holographic display
        self.holographic_canvas = tk.Canvas(
            holographic_frame,
            bg="#000000",
            highlightthickness=1,
            highlightbackground="#00ffff"
        )
        self.holographic_canvas.pack(fill=tk.BOTH, expand=True)

        # Holographic controls
        holographic_controls_frame = ttk.LabelFrame(holographic_frame, text="Holographic Controls", padding="10")
        holographic_controls_frame.pack(fill=tk.X, pady=(10, 0))

        self.holographic_status_var = tk.StringVar(value="IDLE")
        status_label = ttk.Label(
            holographic_controls_frame,
            text="Status:",
            font=("Arial", 10, "bold")
        )
        status_label.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.status_combobox = ttk.Combobox(
            holographic_controls_frame,
            textvariable=self.holographic_status_var,
            values=["IDLE", "LISTENING", "THINKING", "SPEAKING", "WORKING", "ERROR"],
            state="readonly",
            width=20
        )
        self.status_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.status_combobox.current(0)
        self.status_combobox.bind("<<ComboboxSelected>>", self.on_hologram_state_changed)

        # State-specific controls
        self.state_controls_frame = ttk.LabelFrame(
            holographic_controls_frame,
            text="State Controls",
            padding="10"
        )
        self.state_controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.color_label = ttk.Label(
            self.state_controls_frame,
            text="Color:",
            font=("Arial", 9)
        )
        self.color_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.color_entry = ttk.Entry(
            self.state_controls_frame,
            width=10
        )
        self.color_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.color_entry.insert(0, "#00ffff")

        self.glow_label = ttk.Label(
            self.state_controls_frame,
            text="Glow:",
            font=("Arial", 9)
        )
        self.glow_label.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.glow_scale = ttk.Scale(
            self.state_controls_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL
        )
        self.glow_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.glow_scale.set(0.5)

        # Action buttons
        button_frame = ttk.Frame(self.state_controls_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.apply_state_button = ttk.Button(
            button_frame,
            text="Apply State",
            command=self.apply_hologram_state
        )
        self.apply_state_button.pack(side=tk.LEFT, padx=5)

        self.reset_state_button = ttk.Button(
            button_frame,
            text="Reset State",
            command=self.reset_hologram_state
        )
        self.reset_state_button.pack(side=tk.LEFT, padx=5)

        # Voice and system controls
        controls_frame = ttk.LabelFrame(content_frame, text="Voice & System Controls", padding="10")
        controls_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))

        # Voice interface controls
        voice_frame = ttk.LabelFrame(controls_frame, text="Voice Interface", padding="10")
        voice_frame.pack(fill=tk.X, pady=(0, 10))

        self.voice_status_label = ttk.Label(
            voice_frame,
            text="Voice: INACTIVE",
            font=("Arial", 10),
            foreground="red"
        )
        self.voice_status_label.pack(anchor=tk.W, pady=5)

        self.start_voice_button = ttk.Button(
            voice_frame,
            text="Start Voice",
            command=self.start_voice_interface
        )
        self.start_voice_button.pack(fill=tk.X, pady=5)

        self.stop_voice_button = ttk.Button(
            voice_frame,
            text="Stop Voice",
            command=self.stop_voice_interface,
            state=tk.DISABLED
        )
        self.stop_voice_button.pack(fill=tk.X, pady=5)

        # System controls
        system_frame = ttk.LabelFrame(controls_frame, text="System Controls", padding="10")
        system_frame.pack(fill=tk.X, pady=(10, 0))

        self.holographic_toggle_button = ttk.Button(
            system_frame,
            text="Start Holographic",
            command=self.toggle_holographic_interface
        )
        self.holographic_toggle_button.pack(fill=tk.X, pady=5)

        # Log area
        log_frame = ttk.LabelFrame(content_frame, text="System Log", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(10, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(
            log_frame,
            height=20,
            font=("Consolas", 9),
            bg="#1a1a1a",
            fg="#00ff00",
            state=tk.DISABLED
        )
        log_scrollbar = ttk.Scrollbar(
            log_frame,
            orient=tk.VERTICAL,
            command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Log initial message
        self.log_message("JARVIS Enhanced GUI initialized successfully")

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 0))

        self.system_status_label = ttk.Label(
            status_frame,
            text="System Status: Ready",
            font=("Arial", 9),
            foreground="green"
        )
        self.system_status_label.pack(side=tk.LEFT)

        self.time_label = ttk.Label(
            status_frame,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=("Arial", 9)
        )
        self.time_label.pack(side=tk.RIGHT)

        # Update time periodically
        self.update_time()

    def setup_holographic_renderer(self):
        """Setup holographic renderer"""
        try:
            self.holographic_renderer = HologramRenderer3D()
            self.is_holographic_active = True
            self.holographic_status_label.config(text="Holographic: ACTIVE", foreground="green")
            self.log_message("Holographic renderer initialized successfully")
        except Exception as e:
            self.log_message(f"Warning: Holographic renderer initialization failed: {e}")
            self.is_holographic_active = False
            self.holographic_status_label.config(text="Holographic: UNAVAILABLE", foreground="orange")

    def setup_voice_integration(self):
        """Setup voice integration"""
        try:
            self.voice_integration = JarvisVoiceIntegration(
                mode=VoiceIntegrationMode.HYBRID
            )

            if self.voice_integration.start():
                self.log_message("Voice integration initialized successfully")
            else:
                self.log_message("Warning: Voice integration failed to start")

        except Exception as e:
            self.log_message(f"Error: Voice integration setup failed: {e}")

    def on_hologram_state_changed(self, event=None):
        """Handle hologram state change"""
        state = self.holographic_status_var.get()
        self.current_hologram_state.state = state

        # Update state-specific controls
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, self.current_hologram_state.color)

        self.glow_scale.set(self.current_hologram_state.glow_intensity)

        self.log_message(f"Hologram state changed to: {state}")

    def apply_hologram_state(self):
        """Apply hologram state"""
        if not self.is_holographic_active or not self.holographic_renderer:
            self.log_message("Error: Holographic interface not available")
            return

        # Update hologram state with current UI values
        self.current_hologram_state.color = self.color_entry.get()
        self.current_hologram_state.glow_intensity = self.glow_scale.get()

        # Apply state to holographic renderer
        try:
            self.holographic_renderer.set_model_state(self.current_hologram_state)
            self.log_message(f"Hologram state applied: {self.current_hologram_state.state}")
        except Exception as e:
            self.log_message(f"Error applying hologram state: {e}")

    def reset_hologram_state(self):
        """Reset hologram state to default"""
        self.holographic_status_var.set("IDLE")
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, "#00ffff")
        self.glow_scale.set(0.5)

        # Update current state
        self.current_hologram_state.state = "IDLE"
        self.current_hologram_state.color = "#00ffff"
        self.current_hologram_state.glow_intensity = 0.5
        self.current_hologram_state.animation = "idle"

        self.log_message("Hologram state reset to default")

    def start_voice_interface(self):
        """Start voice interface"""
        if not self.voice_integration:
            self.log_message("Error: Voice integration not available")
            return

        try:
            # This would start voice processing
            self.voice_status_label.config(text="Voice: ACTIVE", foreground="green")
            self.start_voice_button.config(state=tk.DISABLED)
            self.stop_voice_button.config(state=tk.NORMAL)

            self.log_message("Voice interface started successfully")
        except Exception as e:
            self.log_message(f"Error starting voice interface: {e}")

    def stop_voice_interface(self):
        """Stop voice interface"""
        if not self.voice_integration:
            return

        try:
            # This would stop voice processing
            self.voice_status_label.config(text="Voice: INACTIVE", foreground="red")
            self.start_voice_button.config(state=tk.NORMAL)
            self.stop_voice_button.config(state=tk.DISABLED)

            self.log_message("Voice interface stopped")
        except Exception as e:
            self.log_message(f"Error stopping voice interface: {e}")

    def toggle_holographic_interface(self):
        """Toggle holographic interface"""
        if self.is_holographic_active:
            # Stop holographic interface
            if self.holographic_renderer:
                self.holographic_renderer.stop_render_loop()

            self.is_holographic_active = False
            self.holographic_status_label.config(
                text="Holographic: STOPPED",
                foreground="orange"
            )
            self.holographic_toggle_button.config(text="Start Holographic")
            self.log_message("Holographic interface stopped")
        else:
            # Start holographic interface
            if self.holographic_renderer:
                self.holographic_renderer.start_render_loop()

            self.is_holographic_active = True
            self.holographic_status_label.config(
                text="Holographic: ACTIVE",
                foreground="green"
            )
            self.holographic_toggle_button.config(text="Stop Holographic")
            self.log_message("Holographic interface started")

    def log_message(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def cleanup(self):
        """Cleanup resources"""
        self.log_message("Cleaning up resources...")

        if self.voice_integration:
            try:
                self.voice_integration.stop()
            except Exception as e:
                self.log_message(f"Warning: Error stopping voice integration: {e}")

        if self.holographic_renderer:
            try:
                self.holographic_renderer.dispose()
            except Exception as e:
                self.log_message(f"Warning: Error disposing holographic renderer: {e}")

        self.log_message("Cleanup completed")

    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.root.destroy()

def main():
    """Main function for standalone usage"""
    root = tk.Tk()
    app = EnhancedJarvisGUI(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.cleanup()

if __name__ == "__main__":
    main()