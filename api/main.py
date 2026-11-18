# FastAPI service layer for Jarvis cellular assistant

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# Telephony and USSD services from core module
from core.telephony import AndroidTelephonyAdapter
from core.ussd import USSDManager

app = FastAPI(
    title="Jarvis Cellular & USSD Services",
    description="AI assistant for cellular calling and dual-SIM balance management",
    version="2.0.0"
)

# Enable CORS for cross-origin requests
# Wildcard origins cannot be combined with credentialed requests; the
# desktop UI needs neither cookies nor credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resolve tooling relative to the project so the API is not tied to one machine.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _find_adb() -> str:
    for candidate in (
        os.environ.get("JARVIS_ADB_PATH"),
        PROJECT_ROOT / "platform-tools" / "platform-tools" / "adb.exe",
        PROJECT_ROOT / "platform-tools-extracted" / "platform-tools" / "adb.exe",
    ):
        if candidate and Path(candidate).exists():
            return str(candidate)
    return "adb"


ADB_PATH = _find_adb()


def _detect_device_id() -> str:
    configured = os.environ.get("JARVIS_DEVICE_ID")
    if configured:
        return configured
    try:
        result = subprocess.run(
            [ADB_PATH, "devices"], capture_output=True, text=True, timeout=10, check=False
        )
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                return parts[0]
    except (OSError, subprocess.SubprocessError):
        logger.warning("Could not auto-detect an Android device via ADB")
    return ""


DEVICE_ID = _detect_device_id()

# Allow imports of sibling project modules when running via `python api/main.py`
sys.path.insert(0, str(PROJECT_ROOT))

from voice_command_processor import VoiceCommandProcessor
from voice_interface import JarvisVoiceInterface
from jarvis_voice_integration import JarvisVoiceIntegration, VoiceStatus


# ---------------------------------------------------------------------------
# Global voice service instances (lazily initialised on first use)
# ---------------------------------------------------------------------------
_voice_integration: Optional[JarvisVoiceIntegration] = None
_voice_interface: Optional[JarvisVoiceInterface] = None
_command_processor: Optional[VoiceCommandProcessor] = None


def get_voice_integration() -> JarvisVoiceIntegration:
    global _voice_integration
    if _voice_integration is None:
        config_path = str(PROJECT_ROOT / "config" / "voice_config.json")
        _voice_integration = JarvisVoiceIntegration(config_path=config_path, mode=None)
    return _voice_integration


def get_voice_interface() -> JarvisVoiceInterface:
    global _voice_interface
    if _voice_interface is None:
        config_path = str(PROJECT_ROOT / "config" / "voice_config.json")
        _voice_interface = JarvisVoiceInterface(config_path=config_path)
    return _voice_interface


def get_command_processor() -> VoiceCommandProcessor:
    global _command_processor
    if _command_processor is None:
        config_path = str(PROJECT_ROOT / "config" / "voice_config.json")
        _command_processor = VoiceCommandProcessor(config_path=config_path)
    return _command_processor


@app.post("/voice/process")
async def process_voice_command(
    text: str,
    processor: VoiceCommandProcessor = Depends(get_command_processor),
    telephony: AndroidTelephonyAdapter = Depends(get_telephony_service),
):
    """Process a natural-language command via the voice command engine."""
    try:
        logger.info(f"Processing voice command: {text}")
        result = processor.execute_command(text)
        if not result or not result.get("success"):
            # Fallback: try simple keyword matching for cellular commands
            lower = text.lower()
            if "call" in lower and any(c.isdigit() for c in text):
                import re as _re
                match = _re.search(r'[\+]?[\d\-\s]{7,15}', text)
                if match:
                    call_result = telephony.dial(match.group())
                    return {
                        "success": True,
                        "response": f"Initiating call to {match.group()}",
                        "raw": result,
                    }
            if "balance" in lower or "credit" in lower:
                return {"success": True, "response": "Balance check initiated", "raw": result}
            if "hangup" in lower or "end call" in lower:
                telephony.hangup()
                return {"success": True, "response": "Call terminated", "raw": result}
            return {"success": False, "response": "Command not recognised.", "raw": result}
        return {"success": True, "response": result.get("response", ""), "raw": result}
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/listen/start")
async def start_voice_listening():
    """Start continuous voice listening mode."""
    try:
        integration = get_voice_integration()
        integration.start()
        interface = get_voice_interface()
        interface.is_listening = True
        return {"status": "listening_started"}
    except Exception as e:
        logger.error(f"Error starting voice listen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/listen/stop")
async def stop_voice_listening():
    """Stop continuous voice listening mode."""
    try:
        integration = get_voice_integration()
        integration.stop()
        interface = get_voice_interface()
        interface.is_listening = False
        return {"status": "listening_stopped"}
    except Exception as e:
        logger.error(f"Error stopping voice listen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voice/status")
async def get_voice_status():
    """Return current voice engine status."""
    try:
        integration = get_voice_integration()
        vstatus = integration.get_status()
        interface = get_voice_interface()
        return {
            "integration_status": vstatus.value if isinstance(vstatus, VoiceStatus) else str(vstatus),
            "is_listening": getattr(interface, "is_listening", False),
            "is_speaking": getattr(interface, "is_speaking", False),
            "metrics": integration.metrics if hasattr(integration, "metrics") else {},
        }
    except Exception as e:
        logger.warning(f"Could not read voice status: {e}")
        return {
            "integration_status": "unknown",
            "is_listening": False,
            "is_speaking": False,
            "error": str(e),
        }


@app.get("/voice/history")
async def get_voice_history(limit: int = 20):
    """Return recent voice command history."""
    try:
        integration = get_voice_integration()
        history = integration.get_command_history()
        return {"history": history[-limit:] if isinstance(history, list) else []}
    except Exception as e:
        logger.warning(f"Could not read voice history: {e}")
        return {"history": []}


@app.get("/voice/help")
async def get_voice_help():
    """Return available voice command help."""
    try:
        integration = get_voice_integration()
        return {"help": integration.get_help()}
    except Exception as e:
        return {"help": [], "error": str(e)}


def get_telephony_service() -> AndroidTelephonyAdapter:
    """Get telephony service instance"""
    return AndroidTelephonyAdapter(ADB_PATH, DEVICE_ID)

def get_ussd_service() -> USSDManager:
    """Get USSD service instance"""
    return USSDManager(ADB_PATH, DEVICE_ID)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    }

@app.get("/sims")
async def get_sim_details(
    telephony: AndroidTelephonyAdapter = Depends(get_telephony_service),
    ussd: USSDManager = Depends(get_ussd_service)
):
    """Get SIM details for both SIM1 and SIM2"""
    try:
        sim1_details = ussd.get_sim_details("SIM1")
        sim2_details = ussd.get_sim_details("SIM2")

        return {
            "SIM1": {
                "phone_number": sim1_details["phone_number"],
                "network": sim1_details["network"],
                "ussd_code": sim1_details["ussd_code"],
                "sub_id": sim1_details["sub_id"]
            },
            "SIM2": {
                "phone_number": sim2_details["phone_number"],
                "network": sim2_details["network"],
                "ussd_code": sim2_details["ussd_code"],
                "sub_id": sim2_details["sub_id"]
            }
        }
    except Exception as e:
        logger.error(f"Error fetching SIM details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/call")
async def initiate_call(
    target: str,
    telephony: AndroidTelephonyAdapter = Depends(get_telephony_service)
):
    """Initiate a phone call"""
    try:
        logger.info(f"Initiating call to {target}")
        result = telephony.dial(target)

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Call failed: {error_msg}")
            raise HTTPException(status_code=400, detail=f"Call failed: {error_msg}")

        return {
            "status": "call_initiated",
            "target": target,
            "output": result.stdout.strip() if result.stdout else "Call command sent."
        }
    except Exception as e:
        logger.error(f"Error in call endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calls/hangup")
async def terminate_call(
    telephony: AndroidTelephonyAdapter = Depends(get_telephony_service)
):
    """Terminate active call"""
    try:
        logger.info("Terminating active call")
        result = telephony.hangup()

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            logger.error(f"Hangup failed: {error_msg}")
            raise HTTPException(status_code=400, detail=f"Hangup failed: {error_msg}")

        return {
            "status": "call_terminated",
            "output": result.stdout.strip() or "Hang-up key event sent."
        }
    except Exception as e:
        logger.error(f"Error in hangup endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ussd/balance")
async def check_balance(
    sim_id: str = "SIM1",
    ussd: USSDManager = Depends(get_ussd_service)
):
    """Check balance for specified SIM"""
    try:
        logger.info(f"Checking balance for {sim_id}")
        result = ussd.check_balance(sim_id)

        return {
            "status": "balance_check_initiated",
            "sim": result["sim"],
            "network": result["network"],
            "code": result["code"],
            "sub_id": result["sub_id"],
            "message": result["message"]
        }
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_system_status(
    telephony: AndroidTelephonyAdapter = Depends(get_telephony_service)
):
    """Get system status. Degrades gracefully when no phone is attached."""
    call_state = "unavailable"
    adb_connected = False
    try:
        adb_connected = bool(DEVICE_ID)
        if adb_connected:
            call_state = telephony.get_call_state() or "unknown"
    except Exception as e:
        logger.warning(f"Could not read call state: {e}")

    return {
        "status": "system_status",
        "call_state": call_state,
        "device_id": DEVICE_ID or None,
        "adb_connected": adb_connected,
        "timestamp": time.time()
    }

@app.get("/network")
async def detect_network(number: str = "+251954531474"):
    """Detect the operator and USSD code for a phone number."""
    network, ussd_code = USSDManager.identify_network(number)
    return {
        "status": "network_detection",
        "detected_network": network,
        "detected_ussd_code": ussd_code,
        "sample_number": number,
    }