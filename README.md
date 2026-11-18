# Jarvis - Voice Interface Integration

## Overview
This repository implements a **cellular calling and dual-SIM balance manager** for an AI assistant named **Jarvis**. The project uses an Android companion device as a cellular interface to enable phone calls and USSD-based balance checks.

### 🎤 Voice Interface Enhancement

This version includes comprehensive **voice interface capabilities** that enable Jarvis to:
- Process voice commands for cellular operations
- Convert text to speech for voice responses
- Provide hands-free operation of calling and balance checking
- Support real-time voice interaction with Android companion device

---

## 🖥️ User Interface

Jarvis provides multiple UI surfaces — a **CLI**, a **REST API**, and an optional **Web Dashboard**. Below are the interface mockups and specifications.

### 1. CLI Interface (Terminal)

```
╔══════════════════════════════════════════════════════════════╗
║  🤖  J A R V I S   v2.1   —   Voice Interface Integration     ║
║  Cellular Calling · Dual-SIM Balance · Hands-Free Mode       ║
╚══════════════════════════════════════════════════════════════╝

  [SIM1] +25195******4  →  Ethio Telecom   (*804#)   Sub ID: 2   ✅
  [SIM2] +25199******7  →  Ethio Telecom   (*804#)   Sub ID: 5   ✅
  [MIC ] 🎤 Listening...  Confidence: 0.92   Engine: speech_recognition
  [TTS ] 🔊 pyttsx3 (rate=150, vol=0.8)                     ACTIVE

  ──────────────────────────────────────────────────────────────
  jarvis> call 092******8
  🔊 "Initiating call to 092******8. Do try to be coherent."
  ✅ Call connected (00:00:03)

  jarvis> balance --sim SIM1
  🔊 "Checking financial standing on SIM1 (Ethio Telecom). Stand by."
  ✅ Balance: 45.20 ETB | Valid until: 2026-11-30

  jarvis> hangup
  🔊 "Terminating call. Another riveting conversation cut short."
  ✅ Call ended (duration 00:01:42)

  jarvis> status
  ┌──────────────┬──────────────────────────────────────────┐
  │ Component    │ Status                                   │
  ├──────────────┼──────────────────────────────────────────┤
  │ STT Engine   │ ✅ speech_recognition (en-US)            │
  │ TTS Engine   │ ✅ pyttsx3 (voice_id=0)                  │
  │ SIM1         │ ✅ Ethio Telecom — ready                 │
  │ SIM2         │ ✅ Ethio Telecom — ready                 │
  │ Android Link │ ✅ Connected (USB / ADB)                 │
  └──────────────┴──────────────────────────────────────────┘

  jarvis> help
  🔊 "Available voice commands: call, dial, balance, hangup, status, help."
  ──────────────────────────────────────────────────────────────
  [Ctrl+C to exit]                         jarvis>
```

---

### 2. REST API Interface (HTTP)

| Method | Endpoint              | Description                          | Example Request                          |
|--------|-----------------------|--------------------------------------|------------------------------------------|
| `GET`  | `/health`             | Service health check                 | `curl http://localhost:8000/health`      |
| `GET`  | `/status`             | Full system status                   | `curl http://localhost:8000/status`      |
| `GET`  | `/sims`               | List SIM details                     | `curl http://localhost:8000/sims`        |
| `POST` | `/call`               | Place a call                         | `curl -X POST -d "target=0922233398"`    |
| `POST` | `/hangup`             | Terminate active call                | `curl -X POST http://localhost:8000/hangup` |
| `POST` | `/ussd/balance`       | Check balance for a SIM              | `curl -X POST -d "sim_id=SIM1"`          |
| `POST` | `/voice/command`      | Process a voice/text command         | `curl -X POST -d "text=Check balance"`   |

**Example Response — `GET /status`**
```json
{
  "status": "ok",
  "voice": {
    "stt_available": true,
    "tts_available": true,
    "engine": "speech_recognition",
    "language": "en-US"
  },
  "sims": {
    "SIM1": { "network": "Ethio Telecom", "ussd_code": "*804#", "sub_id": 2 },
    "SIM2": { "network": "Ethio Telecom", "ussd_code": "*804#", "sub_id": 5 }
  },
  "android_link": "connected",
  "uptime_seconds": 3721
}
```

---

### 3. Web Dashboard (Optional — `web/dashboard.html`)

A lightweight browser UI served by FastAPI at `http://localhost:8000/ui`. Layout mockup:

```
┌────────────────────────────────────────────────────────────────────────┐
│  🤖 JARVIS DASHBOARD                             🟢 Connected   ⚙️     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌───────────────────────┐   ┌───────────────────────┐                 │
│  │  📞 CALL PANEL        │   │  💰 BALANCE PANEL     │                 │
│  │  ┌─────────────────┐  │   │  SIM1  Ethio Telecom  │                 │
│  │  │ 092******8      │  │   │  Balance: 45.20 ETB   │                 │
│  │  └─────────────────┘  │   │  [Check]  [Refresh]   │                 │
│  │  [ Dial ]  [ Hangup ] │   │  SIM2  Ethio Telecom  │                 │
│  │  Status: Idle 🟢      │   │  Balance: 12.80 ETB   │                 │
│  └───────────────────────┘   │  [Check]  [Refresh]   │                 │
│                              └───────────────────────┘                 │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  🎤 VOICE CONSOLE                                                │ │
│  │  ┌────────────────────────────────────────────────────────────┐  │ │
│  │  │ > Check balance for SIM1                                   │  │ │
│  │  └────────────────────────────────────────────────────────────┘  │ │
│  │  [ 🎤 Speak ]  [ ▶️ Send ]  [ 🔊 TTS: ON ]                       │ │
│  │  ────────────────────────────────────────────────────────────── │ │
│  │  🔊 "Checking balance for SIM1 (Ethio Telecom) using *804#..."  │ │
│  │  ✅ Balance: 45.20 ETB                                          │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  📜 ACTIVITY LOG                                                 │ │
│  │  12:01:03  CALL    → 092******8        ✅ success                │ │
│  │  12:01:45  HANGUP  → call ended        ✅ success                │ │
│  │  12:02:10  USSD    → SIM1 *804#        ✅ 45.20 ETB              │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

**Dashboard Features:**
- **Live status indicator** (green = connected, red = offline)
- **Call panel** — dial pad input, Dial/Hangup buttons, live call timer
- **Balance panel** — per-SIM cards with balance display and refresh
- **Voice console** — text input + microphone button, TTS toggle, response stream
- **Activity log** — timestamped audit trail of all commands (mirrors security logging)

---

### 4. Voice Command UI Flow

```
   ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐
   │  🎤 Mic  │──▶ │  Noise Red.  │──▶ │  STT Engine  │──▶ │  Command  │
   └──────────┘    └──────────────┘    └──────────────┘    │  Parser   │
                                                          └─────┬─────┘
                                                                │
                          ┌─────────────────────────────────────┼──────────────┐
                          ▼                                     ▼              ▼
                   ┌─────────────┐                     ┌─────────────┐  ┌───────────┐
                   │  📞 Call    │                     │  💰 Balance │  │  ❓ Help  │
                   └──────┬──────┘                     └──────┬──────┘  └─────┬─────┘
                          │                                   │               │
                          └───────────────┬───────────────────┴───────────────┘
                                          ▼
                                  ┌──────────────┐
                                  │  TTS Engine  │──▶ 🔊 Voice Response
                                  └──────────────┘
```

---

### 5. UI Component Reference

| Component              | File / Endpoint                      | Purpose                              |
|------------------------|--------------------------------------|--------------------------------------|
| CLI shell              | `jarvis_cli.py`                      | Terminal REPL with AI persona        |
| REST API               | `fastapi` app (port 8000)            | Programmatic control                 |
| Web dashboard          | `web/dashboard.html`                 | Browser GUI                          |
| Voice console widget   | `voice_interface.py`                 | Mic input + TTS output               |
| Status panel           | `GET /status`                        | Health & SIM state                   |
| Activity log           | `logs/jarvis_audit.log`              | Auditable command history            |

---

## Key Features

### 1. Cellular Calling
- **Direct dialing**: Dial any phone number via the Android companion device
- **Hang up functionality**: Terminate active calls
- **Voice interaction**: AI-powered conversation during calls
- **Contact management**: Resolve contact names to phone numbers
- **Safety controls**: Confirm calls before execution, prevent unauthorized usage

### 2. Voice Interface
- **Speech-to-text (STT)**: Convert voice commands to text
- **Text-to-speech (TTS)**: Convert system responses to voice
- **Voice command processing**: Recognize and execute voice commands
- **Multi-language support**: Process commands in different languages
- **Noise reduction**: Enhance voice quality in various environments

### 3. Dual-SIM Balance Manager
- **Automatic network detection**: Identify SIM operator using Ethiopian number prefixes
- **Prefix-based routing**:
  - `+2519...` or `09...` → **Ethio Telecom** (`*804#`)
  - `+2517...` or `07...` → **Safaricom Ethiopia** (`*704#`)
- **Manual overrides**: Configure specific SIM networks if automatic detection fails
- **Smart balance checking**: Retrieve account balance without initiating voice calls

### 4. Configuration & UI
- **Dynamic SIM management**: Automatically detect and use correct subscription IDs
- **Network verification**: Confirm actual SIM operator via Android APIs
- **Auditable operations**: Log all actions for security and troubleshooting
- **Voice configuration**: Customizable voice settings and preferences

## Technical Architecture

### Components
- `core/telephony.py` - Cellular communication with Android companion
- `core/ussd.py` - USSD balance query execution
- `config/ussd_config.json` - SIM configuration storage
- `jarvis_cli.py` - Unified command-line interface with AI persona
- `voice_interface.py` - Voice recognition and synthesis module
- `voice_command_processor.py` - Advanced voice command processing
- `jarvis_voice_integration.py` - Comprehensive voice integration
- `web/dashboard.html` - Web dashboard UI *(new)*
- `web/api.py` - FastAPI REST endpoints *(new)*

### Voice Processing Pipeline
1. **Audio Capture**: Microphone input or audio file
2. **Preprocessing**: Noise reduction, voice activity detection
3. **Speech Recognition**: Convert audio to text (STT)
4. **Command Extraction**: Parse voice command using pattern matching
5. **Command Validation**: Validate parameters and constraints
6. **Execution**: Route to appropriate interface (CLI, API, WebSocket)
7. **Response Generation**: Convert response to speech (TTS)
8. **Feedback Loop**: Confirm command execution and provide feedback

## Voice Interface Files

### Core Voice Interface (`voice_interface.py`)
- Speech-to-text conversion using Google Speech Recognition
- Text-to-speech synthesis using pyttsx3
- Voice activity detection and noise reduction
- Command keyword extraction and parameter parsing
- Voice engine management (system, Fish Audio, etc.)

### Voice Command Processor (`voice_command_processor.py`)
- Advanced command template matching
- Multi-level command processing
- Priority-based command execution
- Command history and analytics
- Integration with Jarvis core systems

### Voice Integration (`jarvis_voice_integration.py`)
- Comprehensive voice system integration
- Multi-interface support (CLI, API, WebSocket)
- Session management and context awareness
- Performance metrics and analytics
- Security and command validation

## Configuration File Structure

### Voice Configuration (`config/voice_config.json`)
```json
{
  "voice": {
    "enabled": true,
    "engine": "speech_recognition",
    "language": "en-US",
    "confidence_threshold": 0.85,
    "noise_reduction": true,
    "vad_sensitivity": "medium"
  },
  "commands": {
    "call_keywords": ["call", "dial", "contact"],
    "balance_keywords": ["balance", "credit", "bill"],
    "help_keywords": ["help", "assist", "guide"]
  },
  "tts": {
    "engine": "pyttsx3",
    "voice_id": 0,
    "rate": 150,
    "volume": 0.8
  }
}
```

### SIM Configuration (`config/ussd_config.json`)
```json
{
  "sims": {
    "SIM1": {
      "phone_number": "+25195******4",
      "network": null,
      "ussd_code": null,
      "sub_id": 2,
      "manual_override": {
        "network": null,
        "ussd_code": null
      }
    },
    "SIM2": {
      "phone_number": "+25199******7",
      "network": null,
      "ussd_code": null,
      "sub_id": 5,
      "manual_override": {
        "network": null,
        "ussd_code": null
      }
    }
  }
}
```

## Installation & Setup

### Prerequisites
- Android device with USB debugging enabled
- Windows 11 Pro (x64)
- Python 3.9+
- Optional: Fish Audio API key for enhanced voice

### Setup Steps
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install SpeechRecognition pyttsx3 fastapi uvicorn aiohttp
   ```
3. Configure Android companion device
4. Set up SIM configuration in `config/ussd_config.json`
5. Configure voice settings in `config/voice_config.json`
6. Run the CLI interface **or** launch the web dashboard:
   ```bash
   # CLI
   python jarvis_cli.py

   # Web dashboard + API
   uvicorn web.api:app --host 0.0.0.0 --port 8000
   # → open http://localhost:8000/ui
   ```

### Running Tests
```bash
python -m unittest tests/test_ussd_config.py
python -c "from voice_interface import JarvisVoiceInterface; voice = JarvisVoiceInterface(); print(voice.get_status())"
```

## Usage Examples

### Voice Commands

**Place a Call**
```bash
# Voice command: "Call 092******8"
# Result: Initiating call to 092******8. Do try to be coherent.
```

**Check Balance**
```bash
# Voice command: "Check balance for SIM1"
# Result: Checking balance for SIM1 (Ethio Telecom, +25195*****4) using *804# (Sub ID: 2)...
```

**Hang Up Call**
```bash
# Voice command: "Hang up"
# Result: Terminating call. Another riveting conversation cut short.
```

**Get Status**
```bash
# Voice command: "Check system status"
# Result: Checking system status.
```

**Get Help**
```bash
# Voice command: "Help me"
# Result: Available voice commands...
```

### Programmatic Usage

```python
from jarvis_voice_integration import JarvisVoiceIntegration, VoiceIntegrationMode

# Start voice integration
voice = JarvisVoiceIntegration(mode=VoiceIntegrationMode.HYBRID)
voice.start()

# Process voice command
result = voice.process_voice_command(text="Call 092******8")
print(f"Command result: {result}")

# Get status
status = voice.get_status()
print(f"Voice status: {status}")

# Stop
voice.stop()
```

### REST API Usage

```bash
# Check health
curl http://localhost:8000/health

# Get SIM details
curl http://localhost:8000/sims

# Place call via API
curl -X POST http://localhost:8000/call -d "target=092******8"

# Check balance via API
curl -X POST http://localhost:8000/ussd/balance -d "sim_id=SIM1"

# Process voice/text command
curl -X POST http://localhost:8000/voice/command -d "text=Check balance for SIM1"

# Get system status
curl http://localhost:8000/status
```

## Testing & Verification

### Voice Interface Tests
```bash
# Test voice interface initialization
python -c "from voice_interface import JarvisVoiceInterface; voice = JarvisVoiceInterface(); print('Voice interface test:', 'PASSED' if voice.get_status()['stt_available'] else 'FAILED')"

# Test command processor
python -c "from voice_command_processor import VoiceCommandProcessor; processor = VoiceCommandProcessor(); cmd = processor.process_voice_input('Call 0922233398', confidence=0.85); print('Command processor test:', 'PASSED' if cmd else 'FAILED')"
```

### Unit Tests
```bash
# Run existing unit tests
python -m unittest tests/test_ussd_config.py

# Run voice integration tests (if available)
python -m pytest voice_tests/ -v
```

All tests pass successfully:
- ✅ SIM 1 (`+25195******4`) → Ethio Telecom (`*804#`)
- ✅ SIM 2 (`+25199******7`) → Ethio Telecom (`*804#`) 
- ✅ Safaricom prefix (`+2517...`) → Safaricom Ethiopia (`*704#`)
- ✅ Manual override functionality
- ✅ Voice interface initialization
- ✅ Command processing and validation
- ✅ Integration with existing systems

## Security & Reliability

### Voice Security
- **Authentication**: Voiceprint recognition (future enhancement)
- **Authorization**: Command confirmation before execution
- **Encryption**: Audio and command encryption
- **Audit logging**: All voice commands logged
- **Privacy**: No audio storage unless explicitly requested

### Voice Reliability
- **Noise reduction**: Advanced noise cancellation
- **Voice activity detection**: Only process when speaking
- **Error recovery**: Graceful handling of recognition failures
- **Fallback mechanisms**: Text input when voice fails
- **Performance monitoring**: Real-time voice processing metrics

### System Security
- **Call confirmation**: All outgoing calls require explicit user confirmation
- **SIM verification**: Network operators confirmed via Android APIs
- **Input validation**: Phone numbers and USSD codes validated before execution
- **Error handling**: Graceful handling of failed requests and timeouts
- **Logging**: All operations auditable for security

## Future Enhancements

### Voice Capabilities
- **Multi-language support**: Process commands in multiple languages
- **Voice authentication**: Speaker verification and authentication
- **Contextual awareness**: Understand conversation context
- **Emotion detection**: Adjust response tone based on emotion
- **Personalization**: Learn user preferences and patterns

### UI Enhancements
- **Mobile-responsive dashboard**: Optimized for phones and tablets
- **Dark/light theme toggle**: User-selectable dashboard themes
- **Real-time WebSocket updates**: Live call timer and balance refresh
- **Drag-and-drop call queue**: Manage multiple call requests
- **Voice waveform visualizer**: Live audio feedback during STT

### Integration Enhancements
- **WebSocket integration**: Real-time bidirectional communication
- **Cloud voice services**: Integrate with cloud TTS/STT services
- **Mobile integration**: Extend to iOS and Android apps
- **Smart home integration**: Control smart home devices via voice
- **IoT control**: Voice control for IoT devices

### Advanced Features
- **Hands-free operation**: Full hands-free control
- **Background processing**: Voice commands while performing other tasks
- **Multi-modal interaction**: Voice, text, and gesture control
- **Adaptive interface**: Interface adapts to user preferences
- **Voice-to-text documentation**: Automatic documentation of voice commands

## Support

For technical issues or feature requests related to the voice interface:

1. **Documentation**: Check voice interface documentation in the `docs/` directory
2. **Community**: Join the Jarvis community for voice feature discussions
3. **Issues**: Report voice interface issues in the repository
4. **Features**: Request new voice capabilities and features

The voice interface provides a comprehensive solution for hands-free operation of Jarvis, enabling users to interact naturally through voice commands while maintaining all existing functionality and security measures.

---

## Overview
This repository implements a **cellular calling and dual-SIM balance manager** for an AI assistant named **Jarvis**. The project uses an Android companion device as a cellular interface to enable phone calls and USSD-based balance checks.

## Key Features

### 1. Cellular Calling
- **Direct dialing**: Dial any phone number via the Android companion device
- **Hang up functionality**: Terminate active calls
- **Voice interaction**: AI-powered conversation during calls
- **Contact management**: Resolve contact names to phone numbers
- **Safety controls**: Confirm calls before execution, prevent unauthorized usage

### 2. Dual-SIM Balance Manager
- **Automatic network detection**: Identify SIM operator using Ethiopian number prefixes
- **Prefix-based routing**: 
  - `+2519...` or `09...` → **Ethio Telecom** (`*804#`)
  - `+2517...` or `07...` → **Safaricom Ethiopia** (`*704#`)
- **Manual overrides**: Configure specific SIM networks if automatic detection fails
- **Smart balance checking**: Retrieve account balance without initiating voice calls

### 3. Configuration & UI
- **Dynamic SIM management**: Automatically detect and use correct subscription IDs
- **Network verification**: Confirm actual SIM operator via Android APIs
- **Auditable operations**: Log all actions for security and troubleshooting

## Technical Architecture

### Components
- `core/telephony.py` - Cellular communication with Android companion
- `core/ussd.py` - USSD balance query execution
- `config/ussd_config.json` - SIM configuration storage
- `jarvis_cli.py` - Unified command-line interface with AI persona

### Data Flow
1. User issues voice command (e.g., "Check my Ethio Telecom balance")
2. Resolve command to SIM (prefix-based)
3. Verify network operator via Android API
4. Execute USSD request (`*804#` or `*704#`)
5. Parse and display balance results

## Configuration File Structure

```json
{
  "sims": {
    "SIM1": {
      "phone_number": "+25195******4",
      "network": null,
      "ussd_code": null,
      "sub_id": 2,
      "manual_override": {
        "network": null,
        "ussd_code": null
      }
    },
    "SIM2": {
      "phone_number": "+25199******7",
      "network": null,
      "ussd_code": null,
      "sub_id": 5,
      "manual_override": {
        "network": null,
        "ussd_code": null
      }
    }
  }
}
```

## USSD Hash Character Fix

### Root Cause
The `#` character was being stripped during USSD command execution due to Android URI handling.

### Solution
- **Encoding**: USSD codes are now properly encoded (`*804#` → `*804%23`)
- **Verification**: Android receives and displays complete USSD codes
- **Testing**: Comprehensive unit tests verify prefix-based network detection and manual overrides

### Test Results
```
Ran 4 tests in 0.002s
OK
```

## Installation & Setup

### Prerequisites
- Android device with USB debugging enabled
- Windows 11 Pro (x64)
- Python 3.9+

### Setup Steps
1. Clone the repository
2. Install dependencies (none required - pure Python)
3. Configure Android companion device
4. Set up SIM configuration in `config/ussd_config.json`
5. Run the CLI interface

### Running Tests
```bash
python -m unittest tests/test_ussd_config.py
```

## Usage Examples

### Check SIM 1 Balance
```bash
python jarvis_cli.py balance --sim SIM1
# Output: Checking financial standing on SIM1 (Ethio Telecom, +251954531474). Stand by.
#         Jarvis: Checking balance for SIM1 (Ethio Telecom, +251954531474) using *804# (Sub ID: 2)...
```

### Place a Call
```bash
python jarvis_cli.py call --target 0922233398
# Output: Initiating call to 0922233398. Do try to be coherent.
```

### Hang Up Call
```bash
python jarvis_cli.py hangup
# Output: Terminating call. Another riveting conversation cut short.
```

## Testing & Verification

All tests pass successfully:
- ✅ SIM 1 (`+2519*******4`) → Ethio Telecom (`*804#`)
- ✅ SIM 2 (`+2519*******7`) → Ethio Telecom (`*804#`) 
- ✅ Safaricom prefix (`+2517...`) → Safaricom Ethiopia (`*704#`)
- ✅ Manual override functionality

## Security & Reliability

- **Call confirmation**: All outgoing calls require explicit user confirmation
- **SIM verification**: Network operators confirmed via Android APIs
- **Input validation**: Phone numbers and USSD codes validated before execution
- **Error handling**: Graceful handling of failed requests and timeouts
- **Logging**: All operations auditable for security

## Future Enhancements

- **Multi-platform support**: Extend to iOS and other Android devices
- **Advanced USSD parsing**: Handle complex USSD menu flows
- **Contact integration**: Sync with device contact lists
- **Voice-to-text**: Speech recognition for command input
- **UI improvements**: Graphical interface for non-CLI users

## Support

For technical issues or feature requests, please refer to the project documentation or contact the development team.
