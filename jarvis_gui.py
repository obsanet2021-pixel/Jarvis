import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.simpledialog import askstring

BASE_DIR = Path(__file__).resolve().parent
SHELL_SCRIPT = BASE_DIR / "jarvis_shell.py"
SHELL_TIMEOUT_SECONDS = 20

COLOR_OK = "#27AE60"
COLOR_ERROR = "#E74C3C"
COLOR_WARN = "#F39C12"
COLOR_IDLE = "#2E86C2"


class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS - AI Cellular Assistant")
        self.root.geometry("820x660")
        self.root.minsize(680, 540)

        self.current_status = "READY"
        self.busy = False
        self.action_buttons = []

        self.create_interface()
        self.update_info_text(self.default_info_text())

    @staticmethod
    def default_info_text():
        return (
            "System: Jarvis Cellular\n"
            "Version: 2.0.0\n"
            f"Shell: {SHELL_SCRIPT.name}\n"
            "Device state: unknown (run Check Status)\n"
            "Balance: unknown (run Check Balance)\n"
            f"Python: {sys.version.split()[0]}\n"
        )

    def create_interface(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        for row in range(7):
            main_frame.rowconfigure(row, weight=0)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=1)

        title_label = ttk.Label(
            main_frame,
            text="JARVIS - AI Cellular Assistant",
            font=("Arial", 16, "bold"),
            foreground=COLOR_IDLE,
        )
        title_label.grid(row=0, column=0, pady=(0, 16))

        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="15")
        status_frame.grid(row=1, column=0, sticky="ew", pady=8)
        status_frame.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            status_frame,
            text="Status: READY",
            font=("Arial", 12),
            foreground=COLOR_IDLE,
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.status_detail_label = ttk.Label(
            status_frame,
            text="Idle",
            font=("Arial", 10),
            foreground="#7F8C8D",
        )
        self.status_detail_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="15")
        info_frame.grid(row=2, column=0, sticky="ew", pady=8)
        info_frame.columnconfigure(0, weight=1)

        self.info_text = tk.Text(
            info_frame,
            height=6,
            font=("Consolas", 10),
            bg="#F8F9FA",
            relief="solid",
            borderwidth=1,
        )
        self.info_text.grid(row=0, column=0, sticky="ew")
        self.info_text.config(state=tk.DISABLED)

        control_frame = ttk.LabelFrame(main_frame, text="Control Commands", padding="15")
        control_frame.grid(row=3, column=0, sticky="ew", pady=8)

        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.status_button = ttk.Button(
            buttons_frame, text="Check Status", command=self.check_system_status
        )
        self.status_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.call_button = ttk.Button(
            buttons_frame, text="Make Call", command=self.make_call_dialog
        )
        self.call_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.balance_button = ttk.Button(
            buttons_frame, text="Check Balance", command=self.check_balance_dialog
        )
        self.balance_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.hangup_button = ttk.Button(
            buttons_frame, text="Hang Up Call", command=self.hangup_call
        )
        self.hangup_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.action_buttons = [
            self.status_button,
            self.call_button,
            self.balance_button,
            self.hangup_button,
        ]

        log_frame = ttk.LabelFrame(main_frame, text="Action Log", padding="15")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=8)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=("Consolas", 10),
            bg="#2C3E50",
            fg="#ECF0F1",
            relief="solid",
            borderwidth=1,
            wrap="word",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)

        log_scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        output_frame = ttk.LabelFrame(main_frame, text="System Output", padding="15")
        output_frame.grid(row=5, column=0, sticky="nsew", pady=8)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_frame,
            height=6,
            font=("Consolas", 10),
            bg="#FFFFFF",
            relief="solid",
            borderwidth=1,
            wrap="word",
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_text.config(state=tk.DISABLED)

        output_scrollbar = ttk.Scrollbar(
            output_frame, orient=tk.VERTICAL, command=self.output_text.yview
        )
        output_scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        help_frame = ttk.Frame(main_frame)
        help_frame.grid(row=6, column=0, sticky="ew", pady=(8, 0))
        help_frame.columnconfigure(0, weight=1)

        help_text = ttk.Label(
            help_frame,
            text=f"Shell: python {SHELL_SCRIPT.name} help | Logs saved below",
            font=("Arial", 10),
            foreground="#7F8C8D",
        )
        help_text.grid(row=0, column=0, sticky="w")

        self.exit_button = ttk.Button(
            help_frame, text="Exit Jarvis", command=self.confirm_exit
        )
        self.exit_button.grid(row=0, column=1, sticky="e")

        self.append_log("System initialized successfully.")
        self.append_output("Ready to process commands...")

    def append_text(self, widget, message):
        widget.config(state=tk.NORMAL)
        widget.insert(tk.END, message)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

    def append_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_text(self.log_text, f"[{timestamp}] {message.rstrip()}\n")

    def append_output(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_text(self.output_text, f"[{timestamp}] {message.rstrip()}\n")

    def update_info_text(self, text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state=tk.DISABLED)

    def update_log(self, message):
        self.append_log(message)

    def update_output(self, message):
        self.append_output(message)

    def set_status(self, status, color, detail=None):
        self.current_status = status
        self.status_label.config(text=f"Status: {status}", foreground=color)
        if detail is not None:
            self.status_detail_label.config(text=detail)

    def set_buttons_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        for button in self.action_buttons:
            button.config(state=state)

    def run_shell_command(self, label, args, timeout=SHELL_TIMEOUT_SECONDS):
        if self.busy:
            self.append_log(f"[BUSY] {label} skipped, a command is already running.")
            return

        if not SHELL_SCRIPT.exists():
            self.append_log(f"[ERROR] Shell not found at {SHELL_SCRIPT}")
            self.update_output(f"Missing shell script: {SHELL_SCRIPT}")
            self.set_status("ERROR", COLOR_ERROR, "Shell script missing")
            return

        self.busy = True
        self.set_buttons_enabled(False)
        self.set_status("RUNNING", COLOR_WARN, label)
        self.append_log(f"Executing: {label}")

        worker = threading.Thread(
            target=self._execute_shell,
            args=(label, args, timeout),
            daemon=True,
        )
        worker.start()

    def _execute_shell(self, label, args, timeout):
        try:
            result = subprocess.run(
                [sys.executable, str(SHELL_SCRIPT), *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(BASE_DIR),
                timeout=timeout,
            )
            if result.returncode == 0:
                output = (result.stdout or "").strip() or f"{label} completed."
                self.root.after(0, self._on_command_success, label, output)
            else:
                error = (result.stderr or "").strip() or (
                    result.stdout or ""
                ).strip() or f"exit code {result.returncode}"
                self.root.after(0, self._on_command_failure, label, error)
        except subprocess.TimeoutExpired:
            self.root.after(
                0,
                self._on_command_failure,
                label,
                f"timed out after {timeout} seconds",
            )
        except Exception as exc:
            self.root.after(0, self._on_command_failure, label, str(exc))

    def _on_command_success(self, label, output):
        self.append_output(output)
        self.append_log(f"[SUCCESS] {label} completed.")
        self.set_status("OK", COLOR_OK, f"Last action: {label}")
        self._finish_command()

    def _on_command_failure(self, label, error):
        self.append_output(f"{label} failed: {error}")
        self.append_log(f"[ERROR] {label} failed: {error}")
        self.set_status("ERROR", COLOR_ERROR, f"Last action: {label}")
        self._finish_command()

    def _finish_command(self):
        self.busy = False
        self.set_buttons_enabled(True)

    def check_system_status(self):
        self.run_shell_command("Status check", ["status"], timeout=10)

    def make_call_dialog(self):
        phone_number = askstring(
            "Make Call", "Enter phone number:", initialvalue="1234567890"
        )
        if not phone_number:
            return

        cleaned = phone_number.strip().replace(" ", "").replace("-", "")
        if not cleaned.lstrip("+").isdigit() or len(cleaned.lstrip("+")) < 3:
            messagebox.showwarning(
                "Invalid Number",
                "Enter a valid phone number containing digits only "
                "(an optional leading + is allowed).",
            )
            return

        self.run_shell_command(f"Call to {cleaned}", ["call", "--target", cleaned])

    def check_balance_dialog(self):
        sim = askstring("Check Balance", "SIM to check (SIM1 or SIM2):", initialvalue="SIM1")
        if not sim:
            return

        sim_name = sim.strip().upper()
        if sim_name not in ("SIM1", "SIM2"):
            messagebox.showwarning("Invalid SIM", "Choose either SIM1 or SIM2.")
            return

        self.run_shell_command(f"Balance check ({sim_name})", ["balance", "--sim", sim_name])

    def hangup_call(self):
        self.run_shell_command("Hang up call", ["hangup"], timeout=10)

    def confirm_exit(self):
        if messagebox.askyesno("Exit Jarvis", "Are you sure you want to exit Jarvis?"):
            self.root.destroy()

    def on_closing(self):
        self.confirm_exit()


def main():
    root = tk.Tk()
    app = JarvisGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
