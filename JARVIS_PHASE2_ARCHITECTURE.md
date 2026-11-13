# JARVIS_PHASE2_ARCHITECTURE.md
## Overview
This document outlines the technical architecture for integrating Roamies into the existing Jarvis cellular assistant system. The goal is to leverage Roamies' advanced desktop control and AI orchestration capabilities while preserving and extending the existing proven Python telephony adapter and USSD balance manager.

## Recommended Architecture
**Approach B: Hybrid Integration** - Integrate Roamies' AI agent and desktop-control components into the existing Jarvis architecture while maintaining the proven Python telephony adapter.

## Core Components

### 1. AI Orchestrator
**Existing:** Python-based CLI interface (`jarvis_cli.py`)
**Proposed:** Enhanced with Roamies-sidecar agent orchestration

**Implementation:**
```python
# jarvis_cli.py (extended)
from roamies_py import AIOrchestrator  # Bridge to Roamies agent
```

**Responsibilities:**
- Coordinate tool execution between CLI and AI agent
- Manage conversation flow and intent detection
- Interface with all subsystems

### 2. Voice and Speech Engine
**Existing:** Command-line only (text-based)
**Proposed:** Roamies voice integration via Fish Audio

**Implementation:**
```python
# Roamies integration
from roamies_py import VoiceInterface
voice = VoiceInterface(FishAudioKey, language="en")
```

**Responsibilities:**
- Speech-to-text for voice commands
- Text-to-speech for Jarvis responses
- Voice activity detection

### 3. Persistent Memory
**Existing:** No persistent storage
**Proposed:** Roamies memory system

**Implementation:**
```python
# Roamies memory integration
from roamies_py import MemorySystem
memory = MemorySystem(storage_path="~/.jarvis")
```

**Responsibilities:**
- Store conversation history
- Save user preferences and commitments
- Maintain context across sessions

### 4. Windows Computer Control Engine
**Existing:** Python ADB commands for Android interface
**Proposed:** Roamies Windows automation (Tauri Rust backend)

**Implementation:**
```python
# Use Roamies for local Windows control
from roamies_py import DesktopController
desktop = DesktopController(enable_ui_automation=True)
```

**Responsibilities:**
- Windows application automation
- Screen reading and OCR
- UI interaction and clicking

### 5. Filesystem Manager
**Existing:** Python file operations
**Proposed:** Roamies filesystem integration

**Implementation:**
```python
# Roamies for complex file operations
from roamies_py import FileManager
files = FileManager()
```

**Responsibilities:**
- File search and management
- Path resolution for open/save operations
- File type detection and associations

### 6. Background Task Scheduler
**Existing:** No scheduling system
**Proposed:** Roamies task scheduler

**Implementation:**
```python
# Roamies task orchestration
from roamies_py import TaskScheduler
tasks = TaskScheduler()
```

**Responsibilities:**
- Scheduled reminders and notifications
- Background task execution
- Timer-based actions

### 7. Gmail Integration
**Existing:** No email integration
**Proposed:** Roamies Gmail API integration

**Implementation:**
```python
# Roamies for email operations
from roamies_py import GmailAPI
gmail = GmailAPI(auth_provider="oauth")
```

**Responsibilities:**
- Email search and filtering
- Email composition and sending
- Attachment handling

### 8. Google Calendar Integration
**Existing:** No calendar integration
**Proposed:** Roamies Calendar API integration

**Implementation:**
```python
# Roamies for calendar operations
from roamies_py import CalendarAPI
calendar = CalendarAPI(auth_provider="oauth")
```

**Responsibilities:**
- Calendar event management
- Schedule viewing and editing
- Reminders and notifications

### 9. Telegram Messaging
**Existing:** No messaging integration
**Proposed:** Roamies Telegram integration

**Implementation:**
```python
# Roamies for Telegram
from roamies_py import TelegramAPI
telegram = TelegramAPI(bot_token="YOUR_BOT_TOKEN")
```

**Responsibilities:**
- Chat message handling
- Group management
- Message forwarding

### 10. Android SMS Integration
**Existing:** Python ADB for SIM operations
**Proposed:** Roamies SMS abstraction

**Implementation:**
```python
# Roamies for SMS via Android
from roamies_py import SMSSender
sms = SMSSender(adb_path="path/to/adb")
```

**Responsibilities:**
- SMS composition and sending
- Contact resolution for SMS
- SMS threading

### 11. Permission Enforcement Architecture
**Existing:** Basic permission levels
**Proposed:** Advanced permission operating modes

**Implementation:**
```python
# New permission system
from roamies_py import PermissionService
from roamies_py import DelegationPolicy

permission_service = PermissionService()
delegation_policy = DelegationPolicy(
    storage_path="~/.jarvis/policies",
    enforcement_level="hybrid"
)
```

**Responsibilities:**
- Mode-based permission execution (1-5)
- Persistent delegation policy management
- Constraint-based validation
- Intelligent escalation for decision boundaries
- Audit logging and compliance tracking

### 12. Unified AI Tool Orchestration
**Existing:** CLI command dispatcher
**Proposed:** Roamies agent orchestration

**Implementation:**
```python
# Unified tool orchestrator
from roamies_py import ToolOrchestrator
from roamies_py import LLMAccess

orchestrator = ToolOrchestrator()
llm = LLMAccess(api_key="YOUR_API_KEY")
```

**Responsibilities:**
- Tool execution coordination
- Permission management
- API rate limiting
- Error handling and recovery
- Message forwarding

### 10. Android SMS Integration
**Existing:** Python ADB for SIM operations
**Proposed:** Roamies SMS abstraction

**Implementation:**
```python
# Roamies for SMS via Android
from roamies_py import SMSSender
sms = SMSSender(adb_path="path/to/adb")
```

**Responsibilities:**
- SMS composition and sending
- Contact resolution for SMS
- SMS threading

### 11. Cellular Calling
**Existing:** Python ADB-based calling (`core/telephony.py`)
**Proposed:** Enhanced with Roamies

**Implementation:**
```python
# Keep existing Python core, enhance with Roamies
from core.telephony import AndroidTelephonyAdapter
telephony = AndroidTelephonyAdapter(adb_path, device_id)
```

**Responsibilities:**
- Dialing and call management
- USSD balance checking (`*804#`, `*704#`)
- SIM subscription management
- Call state monitoring

### 12. USSD Balance Manager
**Existing:** Python USSD logic (`core/ussd.py`)
**Proposed:** Enhanced with Roamies

**Implementation:**
```python
# Keep existing Python USSD, enhance with Roamies
from core.ussd import USSDManager
ussd = USSDManager(adb_path, device_id)
```

**Responsibilities:**
- Network prefix detection (prefix-based)
- SIM subscription validation
- Balance request and response parsing
- Manual override support

### 13. Unified AI Tool Orchestration
**Existing:** CLI command dispatcher
**Proposed:** Roamies agent orchestration

**Implementation:**
```python
# Unified tool orchestrator
from roamies_py import ToolOrchestrator
from roamies_py import LLMAccess

orchestrator = ToolOrchestrator()
llm = LLMAccess(api_key="YOUR_API_KEY")
```

**Responsibilities:**
- Tool execution coordination
- Permission management
- API rate limiting
- Error handling and recovery

## Service API Specification

### Core Services

#### 1. FastAPI Service (Main Orchestrator)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Jarvis Core Services")

class CallRequest(BaseModel):
    target: str
    sim_id: str = "SIM1"
    confirmation_required: bool = True

class USSDRequest(BaseModel):
    sim_id: str = "SIM1"
    max_retries: int = 1

class AuthRequest(BaseModel):
    api_key: str
    provider: str
```

#### 2. Python Telephony Service
```python
# core/telephony.py - unchanged, exposed via FastAPI
```

#### 3 lậply 3. USSD Service
```python
# core/ussd.py - unchanged, exposed via FastAPI
```

## Integration Sequence

### Phase 1: Foundation Setup
1. **FastAPI Service Layer**
   - Implement core REST API endpoints
   - Add authentication middleware
   - Set up logging and monitoring

2. **Service Registration**
   - Register telephony and USSD services with orchestrator
   - Configure permission levels and access controls

### Phase 2: AI Integration
1. **Roamies Sidecar Connection**
   - Establish Node.js/Python bridge
   - Implement tool discovery and registration
   - Set up message passing protocols

2. **Voice Integration**
   - Configure Fish Audio integration
   - Implement speech-to-text pipeline
   - Set up text-to-speech responses

### Phase 3: Feature Enhancement
1. **New Capabilities**
   - Gmail integration via Roamies APIs
   - Calendar management through Roamies
   - Telegram messaging integration

2. **Advanced Features**
   - Persistent memory with Roamies
   - Background task scheduling
   - Desktop automation with Ro safe boundaries

### Phase 4: Security and Compliance
1. **Permission Model**
   - Implement granular permission system
   - Add approval workflows for sensitive operations
   - Set up audit logging

2. **Safety Measures**
   - Input validation and sanitization
   - Rate limiting and throttling
   - Error handling and recovery

## Security Architecture

### Permission Levels

#### Read-Only Access
- File system read operations
- Email reading and search
- Calendar viewing
- Screen capture and OCR

#### Low-Risk Actions
- Application launching
- File creation in safe directories
- Web browser navigation
- Simple automation tasks

#### Approval Required
- Sending emails
- SMS and Telegram messaging
- Phone calls
- File deletion or modification
- Command execution

#### Strong Confirmation
- Destructive operations
- Sensitive data access
- System configuration changes
- Admin-level operations

### Safety Protocols

#### Input Validation
- Sanitize all external inputs
- Validate file paths and URLs
- Check for injection attempts

#### Error Handling
- Graceful failure recovery
- Comprehensive logging
- User-friendly error messages

#### Rate Limiting
- API call rate limits
- Resource usage monitoring
- Abuse detection and prevention

## AGPL-3.0 Compliance

### License Obligations

**AGPL-3.0 Requirements:**
- Source code must be made available if you distribute modified versions
- Network service use triggers full source code disclosure
- All derived works must use the same license

**Implementation Strategy:**
1. **Internal Use:** Keep existing Python services as-is
2. **Open Services:** If exposing FastAPI endpoints publicly, ensure source code availability
3. **Roamies Integration:** Use Roamies under AGPL-3.0 with proper attribution

### Compliance Checklist

#### ✅ Obligations Met
- All Roamies components used with proper attribution
- Source code maintained and documented
- License terms clearly stated in documentation

#### ⚠️ Considerations
- Modified Roamies code requires AGPL-3.0 compliance
- Derived works from Roamies must be licensed accordingly
- Network services must provide source code access

### License Strategy

**Recommended Approach:**
1. **Keep Python Core:** Maintain existing telephony and USSD as proprietary
2. **Roamies Integration:** Use Roamies as AGPL-3.0 component with clear attribution
3. **Documentation:** Maintain clear licensing documentation
4. **Source Availability:** Ensure compliance tools are in place

## Technical Dependencies

### Required Libraries

#### Python
```python
# Existing dependencies (unchanged)
import subprocess
import json
import time
import argparse
import sys

# New dependencies (added)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio
import aiohttp
```

#### JavaScript/Node.js (Roamies)
```javascript
// Roamies dependencies (from package.json)
"dependencies": {
  "express": "latest",
  "socket.io": "latest",
  "ws": "latest",
  "node-fetch": "latest"
}
```

#### System Tools
- ADB (Android Debug Bridge)
- Python 3.9+
- Node.js 18+
- Rust (for Tauri)

### Optional Dependencies
- Fish Audio API key
- Google API credentials
- Telegram bot tokens
- Email service credentials

## File Structure

```
Jarvis/
├── core/
│   ├── telephony.py          # Python ADB telephony adapter
│   └── ussd.py               # Python USSD balance manager
├── config/
│   └── ussd_config.json      # SIM configuration
├── api/
│   ├── main.py              # FastAPI orchestrator
│   ├── auth.py              # Authentication middleware
│   ├── telephony.py         # Telephony API endpoints
│   └── ussd.py              # USSD API endpoints
├── roamies_bridge.py         # Bridge to Roamies sidecar
├── jarvis_cli.py            # Enhanced CLI with Roamies integration
├── README.md                # Updated documentation
└── ...                     # Additional configuration files
```

## Testing and Verification

### Test Coverage
1. **Unit Tests**
   - Python telephony adapter
   - USSD balance manager
   - API endpoint validation

2. **Integration Tests**
   - FastAPI service communication
   - Roamies sidecar integration
   - End-to-end workflow testing

3. **Security Tests**
   - Input validation testing
   - Permission boundary testing
   - Rate limiting validation

### Testing Strategy

#### Phase 1: Core Services
```bash
# Test telephony service
python -m pytest core/telephony_test.py

# Test USSD service
python -m pytest core/ussd_test.py

# Test API endpoints
python -m pytest api/test_endpoints.py
```

#### Phase 2: Integration
```bash
# Test Roamies integration
python -m pytest integration/roamies_integration_test.py

# Test voice integration
python -m pytest integration/voice_test.py

# Test memory integration
python -m pytest integration/memory_test.py
```

#### Phase 3: End-to-End
```bash
# Full workflow tests
python -m pytest e2e/test_full_workflow.py

# Performance tests
python -m pytest performance/test_performance.py
```

## Migration Plan

### Immediate Actions (Week 1-2)
1. Set up FastAPI service foundation
2. Implement basic API endpoints
3. Test existing Python telephony
4. Create Roamies bridge

### Short-term Actions (Week 3-4)
1. Integrate voice capabilities
2. Add memory system
3. Implement basic authentication
4. Test end-to-end workflows

### Long-term Actions (Month 2+)
1. Add Gmail and Calendar integration
2. Implement advanced automation features
3. Add comprehensive security measures
4. Deploy in production environment

## Risk Mitigation

### Technical Risks
1. **Integration Complexity**
   - Solution: Phase-by-phase integration
   - Mitigation: Thorough testing at each stage

2. **Security Vulnerabilities**
   - Solution: Defense-in-depth approach
   - Mitigation: Comprehensive security testing

3. **Performance Issues**
   - Solution: Load testing and optimization
   - Mitigation: Monitoring and alerting

### License Risks
1. **AGPL-3.0 Compliance**
   - Solution: Legal review and documentation
   - Mitigation: Regular compliance checks

2. **Dependency Conflicts**
   - Solution: Virtual environment management
   - Mitigation: Version pinning and testing

## Success Criteria

### Technical Criteria
- ✅ All existing functionality preserved
- ✅ New capabilities integrated seamlessly
- ✅ Performance meets or exceeds requirements
- ✅ Security measures implemented effectively
- ✅ AGPL-3.0 compliance maintained

### Business Criteria
- ✅ Time-to-market within project timeline
- ✅ Budget constraints respected
- ✅ User experience improved
- ✅ Maintenance and support simplified

### Quality Criteria
- ✅ Code quality and maintainability
- ✅ Testing coverage and reliability
- ✅ Documentation completeness
- ✅ Error handling and recovery

## Conclusion

This Phase 2 architecture document provides a comprehensive plan for integrating Roamies into the existing Jarvis system while maintaining the proven Python telephony adapter. The approach emphasizes:

1. **Modular Integration:** Combine the strengths of both systems
2. **Security-First Design:** Implement robust permission and safety measures
3. **Compliance-Driven Development:** Ensure AGPL-3.0 compliance throughout
4. **Incremental Rollout:** Phase-based deployment to minimize risk
5. **Maintainability:** Clear separation of concerns and documentation

The resulting system will leverage Roamies' advanced AI orchestration and desktop control capabilities while preserving the proven and specialized Python telephony functionality that has been successfully implemented and verified.