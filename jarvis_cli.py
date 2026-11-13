import argparse
import sys

# Project root: C:\Users\Free user\Jarvis
sys.path.insert(0, r"C:\Users\Free user\Jarvis")

from core.telephony import AndroidTelephonyAdapter
from core.ussd import USSDManager


ADB = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
DEVICE = "d12090e57900"


def speak_as_jarvis(message):
    print(f"\n[JARVIS]: {message}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Cellular & USSD Orchestrator"
    )
    parser.add_argument(
        "command",
        choices=["call", "balance", "hangup"],
        help="Action to perform",
    )
    parser.add_argument("--target", help="Phone number to call")
    parser.add_argument(
        "--sim",
        choices=["SIM1", "SIM2"],
        default="SIM1",
        help="SIM to prepare the USSD code for",
    )
    args = parser.parse_args()

    try:
        telephony = AndroidTelephonyAdapter(ADB, DEVICE)
        ussd = USSDManager(ADB, DEVICE)

        if args.command == "call":
            if not args.target:
                parser.error("call requires --target PHONE_NUMBER")

            speak_as_jarvis(f"Initiating call to {args.target}.")
            result = telephony.dial(args.target)
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip())
            print(result.stdout.strip())

        elif args.command == "hangup":
            speak_as_jarvis("Requesting call termination.")
            result = telephony.hangup()
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip())
            print(result.stdout.strip() or "Hang-up key event sent.")

        elif args.command == "balance":
            details = ussd.get_sim_details(args.sim)
            speak_as_jarvis(
                f"Preparing {details['ussd_code']} for {args.sim} "
                f"({details['network']})."
            )
            result = ussd.check_balance(args.sim)
            print(result["message"])
            print(f"Code: {result['code']}")
            print("Please confirm the SIM and tap Call on your phone.")

    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        speak_as_jarvis(f"Operation failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    import subprocess
    raise SystemExit(main())
