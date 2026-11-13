from core.telephony import AndroidTelephonyAdapter
import time

ADB = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
DEVICE = "d12090e57900"
TARGET_NUMBER = "0922233398"

adapter = AndroidTelephonyAdapter(ADB, DEVICE)

print(f"Initiating test call to {TARGET_NUMBER}...")
res = adapter.dial(TARGET_NUMBER)
print(f"Dial command output: {res.stdout}")

time.sleep(3)
print("Checking call state...")
print(f"Call State: {adapter.get_call_state()}")
