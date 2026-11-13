import subprocess
import logging

logger = logging.getLogger(__name__)

def connect_wireless(android_ip: str):
    try:
        # Connect to Android device over TCP/IP
        cmd = [r'C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe', 'connect', f'{android_ip}:5555']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Wireless connection result: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to connect: {e.stderr}")
        return False, e.stderr

if __name__ == '__main__':
    ip = input('Enter Android device IP: ')
    success, msg = connect_wireless(ip)
    print(msg)
