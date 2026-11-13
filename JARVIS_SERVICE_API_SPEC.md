# JARVIS_SERVICE_API_SPEC.md

## Overview
This document specifies the local REST API exposed by the Python telephony and USSD service. It acts as a bridge between the existing Python core (telephony and USSD management) and the Roamies AI agent sidecar / desktop UI.

## Base URL
`http://127.0.0.1:8765` (Localhost only, loopback interface bound).

---

## Security & Authentication
- **Local Loopback Only:** Binds strictly to `127.0.0.1`.
- **Token Authentication:** Every request must include the header:
  `X-Jarvis-Auth: <LOCAL_SECRET_TOKEN>`
- **Rate Limiting:** Maximum 10 requests per minute per IP for sensitive operations (calls, USSD).

---

## Endpoints

### 1. Health Check
- **Path:** `/health`
- **Method:** `GET`
- **Description:** Verifies service status and ADB connection.
- **Request Headers:**
  - `X-Jarvis-Auth: <token>`
- **Response (`200 OK`):**
  ```json
  {
    "status": "healthy",
    "adb_connected": true,
    "device_id": "d12090e57900",
    "timestamp": "2026-11-12T12:00:00Z"
  }
  ```

### 2. Get Active SIMs
- **Path:** `/sims`
- **Method:** `GET`
- **Description:** Returns configured SIMs, network detection, and subscription IDs.
- **Request Headers:**
  - `X-Jarvis-Auth: <token>`
- **Response (`200 OK`):**
  ```json
  {
    "sims": {
      "SIM1": {
        "phone_number": "+251954531474",
        "network": "Ethio Telecom",
        "ussd_code": "*804#",
        "sub_id": 2
      },
      "SIM2": {
        "phone_number": "+251998065377",
        "network": "Ethio Telecom",
        "ussd_code": "*804#",
        "sub_id": 5
      }
    }
  }
  ```

### 3. Place a Cellular Call
- **Path:** `/calls`
- **Method:** `POST`
- **Description:** Initiates an outgoing cellular call via Android ADB. Requires explicit confirmation flag.
- **Request Headers:**
  - `X-Jarvis-Auth: <token>`
  - `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "target": "0922233398",
    "confirmed": true
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "status": "success",
    "message": "Call initiated to 0922233398",
    "target": "0922233398"
  }
  ```
- **Error Response (`400 Bad Request`):**
  ```json
  {
    "error": "Confirmation required before placing a call."
  }
  ```

### 4. Terminate Active Call
- **Path:** `/calls/hangup`
- **Method:** `POST`
- **Description:** Sends hang-up key event to terminate active calls.
- **Request Headers:**
  - `X-Jarvis-Auth: <token>`
- **Response (`200 OK`):**
  ```json
  {
    "status": "success",
    "message": "Hang-up key event sent."
  }
  ```

### 5. Check USSD Balance
- **Path:** `/ussd/balance`
- **Method:** `POST`
- **Description:** Executes USSD balance check code (`*804#` or `*704#`) on the specified SIM with rate limiting to prevent spamming.
- **Request Headers:**
  - `X-Jarvis-Auth: <token>`
  - `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "sim": "SIM1"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "status": "dialer_ready",
    "sim": "SIM1",
    "network": "Ethio Telecom",
    "code": "*804#",
    "sub_id": 2,
    "message": "USSD code entered using Android key events. Verify the dial pad, choose the correct SIM if prompted, and tap Call."
  }
  ```
- **Error Response (`429 Too Many Requests`):**
  ```json
  {
    "error": "Rate limit exceeded. Please wait before executing another USSD query."
  }
  ```
