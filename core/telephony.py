import subprocess


class AndroidTelephonyAdapter:
    def __init__(self, adb_path, device_id):
        self.adb_path = adb_path
        self.device_id = device_id

    def _execute_adb(self, command):
        full_command = [self.adb_path, "-s", self.device_id] + command
        return subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def dial(self, phone_number):
        """Place a normal phone call using Android's CALL intent."""
        number = phone_number.strip().replace(" ", "")
        if not number:
            raise ValueError("A phone number is required.")

        print(f"Jarvis: Dialing {number}...")
        command = [
            "shell", "am", "start",
            "-a", "android.intent.action.CALL",
            "-d", f"tel:{number}",
        ]
        return self._execute_adb(command)

    def hangup(self):
        """Request Android to end the active call."""
        print("Jarvis: Hanging up...")
        return self._execute_adb(["shell", "input", "keyevent", "KEYCODE_ENDCALL"])

    def get_call_state(self):
        """Return call-state lines from dumpsys; output varies by Android version."""
        result = self._execute_adb(["shell", "dumpsys", "telephony.registry"])
        if result.returncode != 0:
            return result.stderr.strip()

        return "\n".join(
            line for line in result.stdout.splitlines()
            if "mCallState" in line or "CallState" in line
        )


if __name__ == "__main__":
    ADB = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
    DEVICE = "d12090e57900"

    adapter = AndroidTelephonyAdapter(ADB, DEVICE)
    print("Testing adapter initialization...")
    print(f"Current call state info: {adapter.get_call_state()}")
