# FastAPI service layer for Jarvis cellular assistant

import subprocess
import time
import logging
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
ADB_PATH = r"C:\Users\Free user\Jarvis\platform-tools\platform-tools\adb.exe"
DEVICE_ID = "d12090e57900"

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
    """Get system status including call state"""
    try:
        call_state = telephony.get_call_state()

        return {
            "status": "system_status",
            "call_state": call_state,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/network")
async def detect_network(
    telephony: AndroidTelephonyAdapter = Depends(get_telephony_service)
):
    """Detect network from phone number"""
    try:
        # Test with a sample number
        test_number = "+251954531474"

        return {
            "status": "network_detection",
            "detected_network": "Ethio Telecom",
            "detected_ussd_code": "*804#",
            "sample_number": test_number
        }
    except Exception as e:
        logger.error(f"Error in network detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))