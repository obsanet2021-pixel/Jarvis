"""
Jarvis Voice Integration Module

Comprehensive voice interface integration for the Jarvis cellular assistant.

This module provides:
- Voice command processing and execution
- Integration with existing CLI and API interfaces
- Real-time voice command handling
- Command confirmation and validation
- Voice command history and analytics
- Multi-interface support (CLI, FastAPI, WebSocket)
"""

import asyncio
import json
import logging
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import queue
import os
import subprocess

# Import local modules
sys.path.insert(0, os.path.dirname(__file__))

class VoiceIntegrationMode(Enum):
    VOICE_ONLY = "voice_only"
    CLI_ONLY = "cli_only"
    API_ONLY = "api_only"
    HYBRID = "hybrid"
    VOICE_FALLBACK = "voice_fallback"

class VoiceCommandSource(Enum):
    MICROPHONE = "microphone"
    TEXT = "text"
    API = "api"
    WEBSOCKET = "websocket"

class VoiceStatus(Enum):
    INACTIVE = "inactive"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"

@dataclass
class VoiceSession:
    id: str
    start_time: datetime
    status: VoiceStatus
    source: VoiceCommandSource
    language: str
    confidence_threshold: float
    commands_processed: int
    last_command: Optional[str]
    current_command: Optional[Dict[str, Any]]
    context: Dict[str, Any]

@dataclass
class VoiceCommandResult:
    success: bool
    command: str
    processed_command: str
    parameters: Dict[str, Any]
    response: str
    execution_time: float
    confidence: float
    timestamp: datetime
    error_message: Optional[str] = None

class JarvisVoiceIntegration:
    """Main voice integration class for Jarvis"""

    def __init__(self, config_path: str = None, mode: VoiceIntegrationMode = VoiceIntegrationMode.HYBRID):
        self.config = self._load_config(config_path)
        self.mode = mode
        self.status = VoiceStatus.INACTIVE
        self.is_active = False
        self.current_session: Optional[VoiceSession] = None
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.callbacks = {}

        # Initialize components
        self.voice_processor = None
        self.command_processor = None
        self.cli_interface = None
        self.api_interface = None
        self.websocket_interface = None

        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Session management
        self.session_history: List[VoiceSession] = []

        # Performance metrics
        self.metrics = {
            'total_commands_processed': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'average_response_time': 0.0,
            'voice_accuracy': 0.0,
            'session_count': 0,
            'uptime_start': datetime.now()
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load voice integration configuration"""
        default_config = {
            "general": {
                "name": "Jarvis Voice Integration",
                "version": "2.0.0",
                "description": "Advanced voice interface for Jarvis cellular assistant",
                "auto_start": False,
                "default_language": "en-US",
                "default_confidence_threshold": 0.85,
                "session_timeout": 300,  # 5 minutes
                "command_timeout": 30,
                "max_sessions": 10
            },
            "voice": {
                "engine": "speech_recognition",
                "sample_rate": 16000,
                "channels": 1,
                "format": "wav",
                "noise_reduction": True,
                "echo_cancellation": True,
                "vad_sensitivity": "medium",
                "language_detection": True,
                "auto_gain_control": True
            },
            "integration": {
                "primary_interface": "cli",  # cli, api, websocket
                "fallback_interfaces": ["api", "websocket"],
                "command_validation": True,
                "command_confirmation": True,
                "interleaved_mode": False,  # Allow voice and CLI commands simultaneously
                "priority_order": ["voice", "cli", "api", "websocket"]
            },
            "commands": {
                "enabled_commands": [
                    "call", "balance", "hangup", "status", "help", "exit",
                    "emergency", "transfer", "hold", "resume"
                ],
                "voice_keywords": {
                    "call": ["call", "dial", "contact", "phone"],
                    "balance": ["balance", "credit", "bill", "charge", "status"],
                    "hangup": ["hangup", "end", "stop", "cancel", "terminate"],
                    "status": ["status", "state", "check", "system", "device"],
                    "help": ["help", "assist", "guide", "support"],
                    "exit": ["exit", "quit", "stop", "goodbye", "off"],
                    "emergency": ["emergency", "urgent", "critical", "help", "sos"]
                },
                "parameter_patterns": {
                    "phone_number": r'(\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}|\d{7,15})',
                    "sim_card": r'(SIM\s*(\d+)|sim\s*(\d+))',
                    "duration": r'(\d+)\s*(?:seconds?|minutes?|mins?|hours?)',
                    "amount": r'(\d+(?:\.\d+)?)\s*(?:dollars?|USD|credits?|units?)'
                }
            },
            "security": {
                "require_confirmation": True,
                "dangerous_commands": ["call", "emergency", "transfer"],
                "max_commands_per_minute": 10,
                "rate_limiting_enabled": True,
                "audit_logging": True,
                "encryption_enabled": True
            },
            "analytics": {
                "enable_command_analytics": True,
                "enable_voice_analytics": True,
                "retention_days": 30,
                "anonymous_reporting": True
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self._deep_merge(default_config, user_config)

        return default_config

    def _deep_merge(self, base_dict: Dict[str, Any], override_dict: Dict[str, Any]):
        """Deep merge two dictionaries"""
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value

    def start(self):
        """Start the voice integration"""
        if self.is_active:
            self.logger.warning("Voice integration already active")
            return False

        try:
            self.logger.info(f"Starting Jarvis Voice Integration in {self.mode.value} mode")

            # Initialize components based on mode
            self._init_components()

            # Start voice interface if needed
            if self.mode in [VoiceIntegrationMode.HYBRID, VoiceIntegrationMode.VOICE_ONLY]:
                self._start_voice_interface()

            # Start API interface if needed
            if self.mode in [VoiceIntegrationMode.HYBRID, VoiceIntegrationMode.API_ONLY]:
                self._start_api_interface()

            # Start CLI interface if needed
            if self.mode in [VoiceIntegrationMode.HYBRID, VoiceIntegrationMode.CLI_ONLY, VoiceIntegrationMode.VOICE_FALLBACK]:
                self._start_cli_interface()

            self.status = VoiceStatus.LISTENING
            self.is_active = True

            self.logger.info("Voice integration started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start voice integration: {e}")
            self.status = VoiceStatus.ERROR
            return False

    def stop(self):
        """Stop the voice integration"""
        if not self.is_active:
            return True

        try:
            self.logger.info("Stopping Jarvis Voice Integration...")

            # Stop all components
            self._stop_voice_interface()
            self._stop_api_interface()
            self._stop_cli_interface()

            # Update current session
            if self.current_session:
                self.current_session.status = VoiceStatus.INACTIVE
                self.session_history.append(self.current_session)
                self.current_session = None

            self.status = VoiceStatus.INACTIVE
            self.is_active = False

            self.logger.info("Voice integration stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping voice integration: {e}")
            return False

    def _init_components(self):
        """Initialize integration components"""
        try:
            # Import and initialize voice processor
            from .voice_interface import JarvisVoiceInterface
            self.voice_processor = JarvisVoiceInterface()

            # Import and initialize command processor
            from .voice_command_processor import VoiceCommandProcessor
            self.command_processor = VoiceCommandProcessor()

            self.logger.info("Voice integration components initialized")

        except ImportError as e:
            self.logger.error(f"Failed to import voice components: {e}")
            raise

    def _start_voice_interface(self):
        """Start voice interface"""
        try:
            # Register voice processor callbacks
            if self.command_processor:
                self.command_processor.register_command_handler(
                    "voice",
                    self._handle_voice_command
                )

            # Start voice recognition if configured
            if self.config["general"]["auto_start"]:
                if self.voice_processor:
                    self.voice_processor.start_listening(self._on_voice_result)

            self.logger.info("Voice interface started")

        except Exception as e:
            self.logger.error(f"Failed to start voice interface: {e}")
            raise

    def _start_api_interface(self):
        """Start API interface"""
        try:
            # Start FastAPI server if needed
            # This would integrate with the existing API
            self.logger.info("API interface started")

        except Exception as e:
            self.logger.error(f"Failed to start API interface: {e}")
            raise

    def _start_cli_interface(self):
        """Start CLI interface"""
        try:
            # Initialize CLI interface
            self.cli_interface = self._create_cli_interface()

            self.logger.info("CLI interface started")

        except Exception as e:
            self.logger.error(f"Failed to start CLI interface: {e}")
            raise

    def _create_cli_interface(self):
        """Create CLI interface"""
        # This would create a CLI interface that can work alongside voice
        return {
            "enabled": True,
            "commands": self.config["commands"]["enabled_commands"],
            "integration_active": True
        }

    def process_voice_command(self, audio_data: bytes = None, text: str = None,
                           source: VoiceCommandSource = VoiceCommandSource.MICROPHONE) -> Optional[VoiceCommandResult]:
        """Process voice command from various sources"""
        if not self.is_active:
            self.logger.warning("Voice integration not active")
            return None

        start_time = time.time()

        try:
            # Convert audio to text if needed
            if audio_data and source == VoiceCommandSource.MICROPHONE:
                if not self.voice_processor:
                    self.logger.error("Voice processor not available")
                    return None

                # Convert audio to text
                text = self._audio_to_text(audio_data)
                if not text:
                    return None

            # Create session if needed
            if not self.current_session:
                self.current_session = self._create_session(source)

            # Process command
            command_result = self._process_text_command(text)

            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(command_result, execution_time)

            # Update session
            if self.current_session and command_result:
                self.current_session.commands_processed += 1
                self.current_session.last_command = text

            # Emit response
            if command_result:
                self._emit_response(command_result)

            return command_result

        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            return None

    def _audio_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert audio data to text"""
        try:
            # Use voice processor if available
            if self.voice_processor:
                # This is a placeholder - actual implementation would depend on the voice engine
                return "sample command text"

            return None

        except Exception as e:
            self.logger.error(f"Error converting audio to text: {e}")
            return None

    def _process_text_command(self, text: str) -> Optional[VoiceCommandResult]:
        """Process text command"""
        if not text or not self.command_processor:
            return None

        try:
            # Use command processor to parse and execute
            if self.command_processor:
                # Process voice input
                command = self.command_processor.process_voice_input(
                    text,
                    confidence=self.config["general"]["default_confidence_threshold"]
                )

                if command:
                    # Execute command
                    result = self.command_processor.execute_command(command)

                    # Convert to VoiceCommandResult
                    voice_result = VoiceCommandResult(
                        success=result.get("status") == "success",
                        command=text,
                        processed_command=command.parsed_command,
                        parameters=command.parameters,
                        response=result.get("output", result.get("message", "Command executed")),
                        execution_time=command.processing_time if command.processing_time else 0.0,
                        confidence=command.confidence,
                        timestamp=datetime.now()
                    )

                    return voice_result

            return None

        except Exception as e:
            self.logger.error(f"Error processing text command: {e}")
            return None

    def _handle_voice_command(self, command):
        """Handle voice command from processor"""
        try:
            # Log the command
            self.logger.info(f"Voice command received: {command.raw_text}")

            # Execute command through appropriate interface
            result = self._execute_command(command)

            # Return result
            return {
                "status": "success",
                "result": result,
                "command": command.raw_text
            }

        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
            return {
                "status": "error",
                "message": str(e),
                "command": command.raw_text if hasattr(command, 'raw_text') else "unknown"
            }

    def _execute_command(self, command) -> Dict[str, Any]:
        """Execute command through appropriate interface"""
        # Determine which interface to use
        primary_interface = self.config["integration"]["primary_interface"]

        if primary_interface == "cli" and self.cli_interface:
            return self._execute_cli_command(command)
        elif primary_interface == "api":
            return self._execute_api_command(command)
        elif primary_interface == "websocket":
            return self._execute_websocket_command(command)
        else:
            # Try all interfaces in order
            for interface in self.config["integration"]["priority_order"]:
                if interface == "cli" and self.cli_interface:
                    result = self._execute_cli_command(command)
                    if result.get("status") != "error":
                        return result
                elif interface == "api":
                    result = self._execute_api_command(command)
                    if result.get("status") != "error":
                        return result
                elif interface == "websocket":
                    result = self._execute_websocket_command(command)
                    if result.get("status") != "error":
                        return result

            return {"status": "error", "message": "No suitable interface found"}

    def _execute_cli_command(self, command) -> Dict[str, Any]:
        """Execute command via CLI"""
        try:
            if not self.cli_interface:
                return {"status": "error", "message": "CLI interface not available"}

            # Format command for CLI
            cmd_parts = ["python", "jarvis_cli.py"]

            # Add command and parameters
            cmd_parts.extend([command.parsed_command])

            for key, value in command.parameters.items():
                if key == "target":
                    cmd_parts.extend(["--target", str(value)])
                elif key == "sim":
                    cmd_parts.extend(["--sim", str(value)])
                elif key == "sim1" or key == "sim2":
                    cmd_parts.extend(["--sim", str(value)])

            # Execute command
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=self.config["general"]["command_timeout"],
                cwd="C:\Users\Free user\Jarvis"
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip()
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr.strip() or "Command failed",
                    "output": result.stdout.strip()
                }

        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_api_command(self, command) -> Dict[str, Any]:
        """Execute command via API"""
        try:
            # This would integrate with the FastAPI server
            # For now, return a placeholder
            return {
                "status": "pending",
                "message": f"API command queued: {command.parsed_command}",
                "parameters": command.parameters
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_websocket_command(self, command) -> Dict[str, Any]:
        """Execute command via WebSocket"""
        try:
            # This would integrate with WebSocket interface
            # For now, return a placeholder
            return {
                "status": "pending",
                "message": f"WebSocket command queued: {command.parsed_command}",
                "parameters": command.parameters
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _create_session(self, source: VoiceCommandSource) -> VoiceSession:
        """Create a new voice session"""
        session_id = f"session_{int(time.time())}_{len(self.session_history)}"

        return VoiceSession(
            id=session_id,
            start_time=datetime.now(),
            status=VoiceStatus.LISTENING,
            source=source,
            language=self.config["general"]["default_language"],
            confidence_threshold=self.config["general"]["default_confidence_threshold"],
            commands_processed=0,
            last_command=None,
            current_command=None,
            context={}
        )

    def _on_voice_result(self, result):
        """Handle voice recognition result"""
        self.logger.info(f"Voice recognition result: {result}")

        # Process the result
        if result and hasattr(result, 'command'):
            # Emit to all registered listeners
            for callback in self.callbacks.values():
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"Error in voice callback: {e}")

    def _emit_response(self, result: VoiceCommandResult):
        """Emit response to registered listeners"""
        try:
            # Add to response queue
            self.response_queue.put(result)

            # Emit to callbacks
            for event, callback in self.callbacks.items():
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"Error emitting response: {e}")

        except Exception as e:
            self.logger.error(f"Error emitting response: {e}")

    def register_callback(self, event: str, callback: Callable):
        """Register callback for voice integration events"""
        self.callbacks[event] = callback
        self.logger.info(f"Registered callback for event: {event}")

    def unregister_callback(self, event: str):
        """Unregister callback"""
        if event in self.callbacks:
            del self.callbacks[event]
        self.logger.info(f"Unregistered callback for event: {event}")

    def get_status(self) -> Dict[str, Any]:
        """Get voice integration status"""
        return {
            "is_active": self.is_active,
            "status": self.status.value,
            "mode": self.mode.value,
            "current_session": {
                "id": self.current_session.id if self.current_session else None,
                "status": self.current_session.status.value if self.current_session else None,
                "commands_processed": self.current_session.commands_processed if self.current_session else 0,
                "last_command": self.current_session.last_command if self.current_session else None
            } if self.current_session else None,
            "metrics": self.metrics,
            "config": self.config
        }

    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command history"""
        if self.command_processor:
            return self.command_processor.get_command_history()
        return []

    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get session history"""
        history = []
        for session in self.session_history:
            history.append({
                "id": session.id,
                "start_time": session.start_time.isoformat(),
                "status": session.status.value,
                "source": session.source.value,
                "language": session.language,
                "commands_processed": session.commands_processed,
                "last_command": session.last_command
            })
        return history

    def _update_metrics(self, result: VoiceCommandResult, execution_time: float):
        """Update performance metrics"""
        self.metrics['total_commands_processed'] += 1

        if result.success:
            self.metrics['successful_commands'] += 1
        else:
            self.metrics['failed_commands'] += 1

        # Update average response time
        total_time = self.metrics['average_response_time'] * (self.metrics['total_commands_processed'] - 1)
        total_time += execution_time
        self.metrics['average_response_time'] = total_time / self.metrics['total_commands_processed']

        # Update session count
        self.metrics['session_count'] = len(self.session_history)

    def _stop_voice_interface(self):
        """Stop voice interface"""
        try:
            if self.voice_processor:
                self.voice_processor.stop_listening()
            self.logger.info("Voice interface stopped")
        except Exception as e:
            self.logger.error(f"Error stopping voice interface: {e}")

    def _stop_api_interface(self):
        """Stop API interface"""
        try:
            # Stop FastAPI server if running
            self.logger.info("API interface stopped")
        except Exception as e:
            self.logger.error(f"Error stopping API interface: {e}")

    def _stop_cli_interface(self):
        """Stop CLI interface"""
        try:
            # Stop CLI interface
            self.logger.info("CLI interface stopped")
        except Exception as e:
            self.logger.error(f"Error stopping CLI interface: {e}")

    def save_config(self, config_path: str):
        """Save configuration to file"""
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            self.logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")

    def load_config(self, config_path: str):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self._deep_merge(self.config, user_config)
            self.logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")

    def get_help(self) -> str:
        """Get help information"""
        help_text = """
Jarvis Voice Integration Help
=============================

Available Commands:
- call <number> - Place a phone call
- balance - Check account balance
- hangup - End current call
- status - Check system status
- help - Show this help
- exit - Exit Jarvis

Voice Commands:
- "Call 0922233398" - Place a call by voice
- "Check balance" - Check balance by voice
- "Hang up" - End call by voice
- "Status" - Check status by voice
- "Help" - Get voice help
- "Exit" - Exit by voice

Integration Modes:
- HYBRID: Voice and CLI interfaces work together
- VOICE_ONLY: Only voice interface enabled
- API_ONLY: Only API interface enabled
- CLI_ONLY: Only CLI interface enabled
- VOICE_FALLBACK: Voice is primary, CLI is fallback

Configuration:
- Check config/vars.py for configuration options
- Save custom configurations to files
- Load configurations from files

Commands can be issued via:
- Microphone (voice)
- Text input
- API calls
- WebSocket connections
"""
        return help_text

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

# Main function for standalone usage
def main():
    """Main function for standalone usage"""
    print("Initializing Jarvis Voice Integration...")

    # Create voice integration
    voice_integration = JarvisVoiceIntegration(
        mode=VoiceIntegrationMode.HYBRID
    )

    # Start integration
    if voice_integration.start():
        print("✅ Jarvis Voice Integration started successfully!")
        print(f"Mode: {voice_integration.mode.value}")
        print(f"Status: {voice_integration.status.value}")

        # Print status
        status = voice_integration.get_status()
        print(f"Active: {status['is_active']}")
        print(f"Current Session: {status['current_session']}")

        # Show help
        print("\n" + voice_integration.get_help())

        try:
            # Keep running
            while voice_integration.is_active:
                # Check for commands
                if not voice_integration.response_queue.empty():
                    response = voice_integration.response_queue.get()
                    print(f"Response: {response.response}")

                # Sleep to prevent busy waiting
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nShutting down...")
            voice_integration.stop()
    else:
        print("❌ Failed to start Jarvis Voice Integration")

if __name__ == "__main__":
    main()