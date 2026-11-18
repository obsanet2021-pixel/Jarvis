"""
install_startup.py — Register JARVIS to launch at Windows login.

Usage:
    python install_startup.py       # default: install
    python install_startup.py --uninstall  # remove shortcut only
    python install_startup.py --help  # show this message

Creates:
  • Desktop shortcut "JARVIS.lnk" -> start_jarvis.ps1
  • Registration in HKCU\\...\\Run -> JARVIS_Startup.bat (auto-starts at login)

Shortcut behavior:
  Double-clicking it opens PowerShell silently (no console window).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT = Path(__file__).resolve().parent
_PYTHON  = _PROJECT / ".wakevenv" / "Scripts" / "python.exe"
_PS1     = _PROJECT / "start_jarvis.ps1"
_BAT     = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) \
           / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "JARVIS_Startup.bat"
_DESKTOP = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"


def _run(cmd: list[str]) -> int:
    """Subprocess.run with check=False; returns exit code."""
    import subprocess
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode


def create_shortcut_on_desktop() -> None:
    """Create a PowerShell shortcut (no console flash) on the desktop."""
    lnk_path = _DESKTOP / "JARVIS.lnk"
    # Use PowerShell's WshShell to create the shortcut — always available on Win10+
    ps_code = rf'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{lnk_path}".Replace('\','\\'))
$Shortcut.TargetPath = "{_PS1}".Replace('\','\\')
$Shortcut.WorkingDirectory = "{_PROJECT}".Replace('\','\\')
$Shortcut.Description = "JARVIS Assistant"
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Save()
'''
    rc = _run([str(_PYTHON), "-c", ps_code])
    if rc != 0:
        print("[ERROR] Failed to create desktop shortcut")
        sys.exit(1)
    print(f"[OK] Desktop shortcut created: {lnk_path}")


def write_startup_batch() -> None:
    """Write a clean startup batch that launches JARVIS headlessly."""
    bat_dir = _BAT.parent
    bat_dir.mkdir(parents=True, exist_ok=True)
    content = (
        "@echo off\n"
        'set JARVIS_DIR=%~dp0..\n'
        "cd /d \"%JARVIS_DIR%\"\n"
        f'"{_PYTHON}" "jarvis_wake.py" --no-gui\n'
        "exit\n"
    )
    _BAT.write_text(content, encoding="utf-8")
    print(f"[OK] Startup batch written: {_BAT}")


def add_registry_autostart() -> None:
    """Register JARVIS_Startup.bat in HKCU Run key for auto-launch at login."""
    run_key = os.path.join(
        "HKEY_CURRENT_USER",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    )
    rc = _run(["reg", "add", run_key, "/v", "JARVIS", "/t", "REG_SZ",
               "/d", str(_BAT), "/f"])
    if rc != 0:
        print("[WARN] Could not write registry autostart entry.")
        print("         Add manually via: reg add \"HKCU\\...\\Run\" /v JARVIS ...")
        return
    print("[OK] Autostart registered (HKCU \\ Windows \\ Run)")


def remove_shortcut() -> bool:
    lnk = _DESKTOP / "JARVIS.lnk"
    if lnk.exists():
        lnk.unlink()
        print(f"[OK] Removed desktop shortcut: {lnk}")
        return True
    print(f"[SKIP] No desktop shortcut found at {lnk}")
    return False


def remove_registry_entry() -> bool:
    run_key = os.path.join(
        "HKEY_CURRENT_USER",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    )
    rc = _run(["reg", "delete", run_key, "/v", "JARVIS", "/f"])
    if rc != 0:
        print("[SKIP] No registry entry found for JARVIS.")
        return False
    print("[OK] Registry autostart entry removed")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install or uninstall JARVIS startup entries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install_startup.py             Install everything (shortcut + autostart)
  python install_startup.py --uninstall Remove only the desktop shortcut
  python install_startup.py --bare      Register autostart without creating shortcut
""",
    )
    parser.add_argument("--uninstall", action="store_true", help="Remove desktop shortcut only")
    parser.add_argument("--bare", action="store_true",
                        help="Only register autostart (skip desktop shortcut)")
    args = parser.parse_args()

    if args.uninstall:
        remove_shortcut()
        return 0

    # Verify prerequisites
    if not _PYTHON.exists():
        print(f"[ERROR] Python not found at {_PYTHON}")
        return 1
    if not _PS1.exists():
        print(f"[ERROR] Launcher not found at {_PS1}")
        return 1

    create_shortcut_on_desktop()

    if not args.bare:
        write_startup_batch()
        add_registry_autostart()
    else:
        write_startup_batch()
        add_registry_autostart()

    print("\n[JARVIS] Installation complete!")
    print("  • Double-click Desktop/JARVIS.lnk to start")
    print("  • Log out/in to verify autostart works")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
