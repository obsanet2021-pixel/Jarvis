import json
import os
import subprocess
import time
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "ussd_config.json"


class USSDManager:
    # Android key codes. Using key events avoids URI parsing of '#'
    # and text-entry interpretation of special characters.
    KEY_CODES = {
        "*": "KEYCODE_STAR",
        "#": "KEYCODE_POUND",
        "0": "KEYCODE_0",
        "1": "KEYCODE_1",
        "2": "KEYCODE_2",
        "3": "KEYCODE_3",
        "4": "KEYCODE_4",
        "5": "KEYCODE_5",
        "6": "KEYCODE_6",
        "7": "KEYCODE_7",
        "8": "KEYCODE_8",
        "9": "KEYCODE_9",
    }

    def __init__(
        self,
        adb_path,
        device_id,
        config_path=None,
    ):
        self.adb_path = adb_path
        self.device_id = device_id
        self.config_path = config_path or os.environ.get(
            "JARVIS_USSD_CONFIG", DEFAULT_CONFIG_PATH
        )
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def identify_network(phone_number):
        """Identify the network using the configured Ethiopian number prefix."""
        clean_num = phone_number.strip().replace(" ", "")
        if clean_num.startswith(("+2519", "09")):
            return "Ethio Telecom", "*804#"
        if clean_num.startswith(("+2517", "07")):
            return "Safaricom Ethiopia", "*704#"
        return "Unknown Network", "*804#"

    def get_sim_details(self, sim_key):
        sims = self.config.get("sims", {})
        if sim_key not in sims:
            raise ValueError(f"Invalid SIM key: {sim_key}")

        sim_info = sims[sim_key]
        phone_number = sim_info["phone_number"]
        override = sim_info.get("manual_override") or {}

        auto_network, auto_code = self.identify_network(phone_number)
        network = (
            override.get("network")
            or sim_info.get("network")
            or auto_network
        )
        ussd_code = (
            override.get("ussd_code")
            or sim_info.get("ussd_code")
            or auto_code
        )

        if not isinstance(ussd_code, str):
            raise ValueError(f"Invalid USSD code configured for {sim_key}.")

        if not ussd_code.startswith("*") or not ussd_code.endswith("#"):
            raise ValueError(
                f"USSD code for {sim_key} must look like *804#; "
                f"received {ussd_code!r}."
            )

        invalid_chars = [char for char in ussd_code if char not in self.KEY_CODES]
        if invalid_chars:
            raise ValueError(
                f"Unsupported character(s) in USSD code: {invalid_chars}"
            )

        return {
            "phone_number": phone_number,
            "network": network,
            "ussd_code": ussd_code,
            "sub_id": sim_info.get("sub_id"),
        }

    def _execute_adb(self, command):
        full_command = [self.adb_path, "-s", self.device_id] + command
        return subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def check_balance(self, sim_key):
        """
        Open the dial pad and enter the USSD code using Android key events.
        The user then confirms the call and selects the intended SIM.
        """
        details = self.get_sim_details(sim_key)
        ussd_code = details["ussd_code"]

        print(
            f"Jarvis: Opening {ussd_code} for {sim_key} "
            f"({details['network']})."
        )

        # Do not put the USSD code in a tel: URI. In particular, '#' can
        # be treated as a URI fragment delimiter by Android.
        result = self._execute_adb([
            "shell", "am", "start",
            "-a", "android.intent.action.DIAL",
        ])
        if result.returncode != 0:
            raise RuntimeError(
                "Could not open Android dialer: "
                + (result.stderr.strip() or result.stdout.strip())
            )

        time.sleep(1.5)

        # Send numeric Android key codes, including STAR and POUND.
        key_events = [
            self.KEY_CODES[character]
            for character in ussd_code
        ]
        result = self._execute_adb([
            "shell", "input", "keyevent",
            *key_events,
        ])

        if result.returncode != 0:
            raise RuntimeError(
                "Could not enter the USSD code: "
                + (result.stderr.strip() or result.stdout.strip())
            )

        return {
            "status": "dialer_ready",
            "sim": sim_key,
            "network": details["network"],
            "code": ussd_code,
            "sub_id": details["sub_id"],
            "message": (
                "USSD code entered using Android key events. "
                "Verify the dial pad, choose the correct SIM if prompted, "
                "and tap Call."
            ),
        }


if __name__ == "__main__":
    ADB = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
    DEVICE = "d12090e57900"

    manager = USSDManager(ADB, DEVICE)
    print("SIM1:", manager.get_sim_details("SIM1"))
    print("SIM2:", manager.get_sim_details("SIM2"))
