import os
import sys
import json
import time
import subprocess
import argparse

sys.path.insert(0, r"C:\Users\Free user\Jarvis")

from core.telephony import AndroidTelephonyAdapter
from core.ussd import USSDManager

ADB = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
DEVICE = "d12090e57900"

def jarvis_speak(msg):
    print(f"\n[JARVIS]: {msg}\n")

def main():
    parser = argparse.ArgumentParser(description="Jarvis CLI Shell")
    parser.add_argument("command", nargs="?", default="help", choices=["call", "hangup", "balance", "status", "help"], help="Command to run")
    parser.add_argument("--target", help="Phone number to call")
    parser.add_argument("--sim", default="SIM1", choices=["SIM1", "SIM2"], help="SIM card to use")

    args = parser.parse_args()
    # Initialize adapters with error handling
    try:
        telephony = AndroidTelephonyAdapter(ADB, DEVICE)
        ussd = USSDManager(ADB, DEVICE)
    except Exception as e:
        jarvis_speak(f"Initialization failed: {e}")
        print(f"Error initializing Jarvis: {e}")
        print("Ensure ADB is available and device is connected.")
        return 1

    if args.command == "call":
        if not args.target:
            print("Error: --target phone_number is required for call.")
            return 1
        jarvis_speak(f"Initiating call to {args.target}.")
        res = telephony.dial(args.target)
        print(res.stdout.strip() if res.stdout else "Dial command sent.")
    elif args.command == "hangup":
        jarvis_speak("Terminating active call.")
        res = telephony.hangup()
        print(res.stdout.strip() if res.stdout else "Hang-up signal sent.")
    elif args.command == "balance":
        try:
            details = ussd.get_sim_details(args.sim)
            jarvis_speak(f"Checking balance for {args.sim} ({details['network']}) using {details['ussd_code']}.")
            res = ussd.check_balance(args.sim)
            print(res["message"])
        except Exception as e:
            jarvis_speak(f"Error checking balance: {e}")
            print(f"Balance check failed: {e}")
    elif args.command == "status":
        jarvis_speak("Checking device status and call state...")
        state = telephony.get_call_state()
        print(state if state else "No active call state detected.")
    else:
        print("""
Jarvis CLI Command Center:
  python jarvis_shell.py call --target <number>
  python jarvis_shell.py hangup
  python jarvis_shell.py balance [--sim SIM1|SIM2]
  python jarvis_shell.py status
  python jarvis_shell.py help
""")
    return 0

if __name__ == "__main__":
    sys.exit(main())
