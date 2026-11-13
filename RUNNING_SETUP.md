# Jarvis Project - Quick Start Guide

## Overview

This document provides quick setup instructions for running the Jarvis cellular assistant system.

## Prerequisites

1. **Hardware**
   - Windows computer with USB port
   - Android device with USB debugging enabled
   - USB cable to connect computer to Android device

2. **Software**
   - Python 3.9+
   - Git

3. **Setup**
   - Install ADB (Android Debug Bridge)
   - Connect Android device and enable USB debugging
   - Pair device with computer

## Quick Start Commands

### 1. Clone the Repository

```bash
cd C:\
git clone https://github.com/kenkaiii/Jarvis.git
```

### 2. Navigate to Project Directory

```bash
cd C:\Users\Free user\Jarvis
```

### 3. Run Core Components

#### Test Telephony Adapter
```bash
python -c "from core.telephony import AndroidTelephonyAdapter; adapter = AndroidTelephonyAdapter(r'C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe', 'd12090e57900'); print('Telephony adapter initialized successfully')"
```

#### Test USSD Manager
```bash
python -c "from core.ussd import USSDManager; manager = USSDManager(r'C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe', 'd12090e57900'); print('USSD manager initialized successfully'); print('SIM1 details:', manager.get_sim_details('SIM1'))"
```

### 4. Launch Jarvis CLI Shell

```bash
python jarvis_shell.py help
```

#### Interactive Usage Examples:

**Check Device Status**
```bash
python jarvis_shell.py status
```

**Make a Call**
```bash
python jarvis_shell.py call --target 5551234567
```

**Check Balance**
```bash
python jarvis_shell.py balance --sim SIM1
```

**Terminate Active Call**
```bash
python jarvir_shell.py hangup
```

### 5. Test API Services (FastAPI)

#### Run FastAPI Server (requires FastAPI and Uvicorn)
```bash
pip install fastapi uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### Test API Endpoints

**Health Check**
```bash
curl -s http://localhost:8000/health | jq
```

**Get SIM Details**
```bash
curl -s http://localhost:8000/sims | jq
```

**Check Balance**
```bash
curl -X POST http://localhost:8000/ussd/balance -H "Content-Type: application/json" -d '{"sim_id": "SIM1"}' | jq
```

### 6. Quick Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `python jarvis_shell.py status` | Check device status | `python jarvis_shell.py status` |
| `python jarvis_shell.py call --target <num>` | Initiate call | `python jarvis_shell.py call --target 1234567890` |
| `python jarvis_shell.py hangup` | Terminate call | `python jarvis_shell.py hangup` |
| `python jarvis_shell.py balance [--sim SIM1|SIM2]` | Check balance | `python jarvis_shell.py balance` |
| `python jarvis_shell.py help` | Show help | `python jarvis_shell.py help` |

### 7. Running Tests

```bash
python -m unittest tests/test_ussd_config.py
```

### 8. Android Integration

**Note:** Android app integration and testing requires additional setup steps not included in this basic guide. See the full documentation for complete Android application setup instructions.

### 9. Development Setup

For development with the FastAPI services:

```bash
# Install Python dependencies
pip install fastapi uvicorn

# Run the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 10. Project Structure

```
Jarvis/
├── core/
│   ├── telephony.py          # Cellular communication with Android
│   └── ussd.py               # USSD balance manager
├── config/
│   └── ussd_config.json      # SIM configuration
├── jarvis_shell.py           # Interactive CLI shell
├── README.md                # Documentation
├── test_call.py             # Testing framework
├── api/                     # FastAPI service layer
│   ├── __init__.py
│   └── main.py             # API endpoints
└── platform-tools/          # ADB tools
```

## Troubleshooting

### ADB Not Found

Ensure ADB is in your PATH or provide the full path in the code.

### Device Not Connected

```bash
adb devices
```

### Permission Errors

Check file permissions and ensure proper access to the project directory.

### FastAPI Server Issues

Ensure port 8000 is not in use or change the port number.

## Support

For technical issues or feature requests, please refer to the project documentation or contact the development team.

## License

This project is part of the Jarvis cellular assistant system. Please refer to the project documentation for specific usage terms and conditions.