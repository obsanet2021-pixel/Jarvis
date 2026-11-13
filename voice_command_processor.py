"""
Voice Command Processor for Jarvis
Advanced Voice Command Recognition and Processing Module

This module provides comprehensive voice command processing for Jarvis, including:
- Multi-level voice command recognition
- Context-aware command processing
- Command validation and execution
- Voice command history and analytics
- Integration with Jarvis core systems
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable

class CommandPriority(Enum):
    IMMEDIATE = "immediate"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

class CommandStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class VoiceCommand:
    id: str
    raw_text: str
    parsed_command: str
    confidence: float
    timestamp: datetime
    priority: CommandPriority
    status: CommandStatus
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    source: str = "voice"
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

@dataclass
class CommandTemplate:
    name: str
    pattern: str
    command_type: str
    priority: CommandPriority
    required_params: List[str]
    optional_params: List[str]
    validation_rules: Dict[str, Any]
    action_mapping: Dict[str, str]
    help_text: str

class VoiceCommandProcessor:
    """Main voice command processing engine for Jarvis"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.command_history: List[VoiceCommand] = []
        self.command_templates: Dict[str, CommandTemplate] = {}
        self.active_commands: Dict[str, VoiceCommand] = {}
        self.command_handlers: Dict[str, Callable] = {}

        # Initialize command templates
        self._init_command_templates()

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Command statistics
        self.stats = {
            'total_commands_processed': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'average_processing_time': 0.0,
            'command_distribution': {}
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load voice command processor configuration"""
        default_config = {
            "command_timeout": 30,
            "max_concurrent_commands": 5,
            "enable_voice_to_text": True,
            "enable_command_validation": True,
            "enable_command_confirmation": True,
            "voice_confidence_threshold": 0.7,
            "duplicate_command_window": 5,
            "max_command_history": 1000,
            "command_retry_attempts": 3,
            "enable_command_analytics": True,
            "enable_context_awareness": True,
            "auto_correct_similar_commands": True,
            "command_logging_level": "detailed"
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def _init_command_templates(self):
        """Initialize command templates for various operations"""

        # Call-related commands
        call_templates = [
            CommandTemplate(
                name="place_call",
                pattern=r"call\s+(?:number\s+)?(\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}|\d{7,15})",
                command_type="telephony",
                priority=CommandPriority.IMMEDIATE,
                required_params=["target"],
                optional_params=["sim", "confirmation_required"],
                validation_rules={
                    "phone_number_validation": True,
                    "sim_validation": ["SIM1", "SIM2"],
                    "max_length": 20
                },
                action_mapping={
                    "jarvis_cli": "call --target {target} --sim {sim}",
                    "fastapi": "/call",
                    "websocket": "call"
                },
                help_text="Place a phone call to the specified number"
            ),

            CommandTemplate(
                name="emergency_call",
                pattern=r"(?:emergency|urgent|immediate)\s+(?:call|dial|contact)\s+(\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}|\d{7,15})",
                command_type="emergency",
                priority=CommandPriority.HIGH,
                required_params=["target"],
                optional_params=["sim"],
                validation_rules={
                    "phone_number_validation": True,
                    "emergency_confirmation": True
                },
                action_mapping={
                    "jarvis_cli": "call --target {target} --sim {sim}",
                    "fastapi": "/call",
                    "websocket": "emergency_call"
                },
                help_text="Place an emergency call (requires confirmation)"
            ),

            CommandTemplate(
                name="call_by_name",
                pattern=r"call\s+(?:contact\s+)?['\"]([^'\"]+)['\"]|call\s+(?:to\s+)?([^\s]+?)(?:\s+on|\s+via|\s+using)?\s*(?:sim\s*(\d+))?",
                command_type="telephony",
                priority=CommandPriority.HIGH,
                required_params=["target"],
                optional_params=["sim", "contact_name"],
                validation_rules={
                    "name_validation": True,
                    "contact_resolution": True,
                    "sim_validation": ["SIM1", "SIM2"]
                },
                action_mapping={
                    "jarvis_cli": "call --target {target} --sim {sim}",
                    "fastapi": "/call",
                    "websocket": "call_by_name"
                },
                help_text="Call a contact by name or alias"
            ),
        ]

        # Balance-related commands
        balance_templates = [
            CommandTemplate(
                name="check_balance",
                pattern=r"(?:check|query|get|verify|see)\s+(?:balance|credit|charge|bill|status)\s*(?:for|on|from)?\s*(?:sim\s*(\d+))?",
                command_type="ussd",
                priority=CommandPriority.HIGH,
                required_params=["sim"],
                optional_params=["all", "details"],
                validation_rules={
                    "sim_validation": ["SIM1", "SIM2", "all"],
                    "balance_type_validation": ["credit", "usage", "data", "all"]
                },
                action_mapping={
                    "jarvis_cli": "balance --sim {sim}",
                    "fastapi": "/ussd/balance",
                    "websocket": "check_balance"
                },
                help_text="Check SIM card balance or credit"
            ),

            CommandTemplate(
                name="detailed_balance",
                pattern=r"(?:detailed|full|complete|comprehensive)\s+(?:balance|credit|status)\s*(?:for|on)?\s*(?:sim\s*(\d+))?",
                command_type="ussd",
                priority=CommandPriority.MEDIUM,
                required_params=["sim"],
                optional_params=["format"],
                validation_rules={
                    "sim_validation": ["SIM1", "SIM2"],
                    "format_validation": ["text", "json", "detailed"]
                },
                action_mapping={
                    "jarvis_cli": "balance --sim {sim}",
                    "fastapi": "/ussd/balance",
                    "websocket": "detailed_balance"
                },
                help_text="Get detailed balance information"
            ),
        ]

        # Call management commands
        call_management_templates = [
            CommandTemplate(
                name="hangup_call",
                pattern=r"(?:hangup|end|call|terminate|stop|cancel|disconnect)\s*(?:call)?",
                command_type="call_control",
                priority=CommandPriority.IMMEDIATE,
                required_params=[],
                optional_params=["confirmation"],
                validation_rules={
                    "confirmation_required": True,
                    "call_active_validation": True
                },
                action_mapping={
                    "jarvis_cli": "hangup",
                    "fastapi": "/calls/hangup",
                    "websocket": "hangup"
                },
                help_text="End the current call"
            ),

            CommandTemplate(
                name="hold_call",
                pattern=r"(?:hold|pause|mute|silence|park)\s*(?:call)?",
                command_type="call_control",
                priority=CommandPriority.MEDIUM,
                required_params=[],
                optional_params=["duration"],
                validation_rules={
                    "call_active_validation": True,
                    "hold_duration_validation": True
                },
                action_mapping={
                    "jarvis_cli": "call --hold",
                    "fastapi": "/call/hold",
                    "websocket": "hold_call"
                },
                help_text="Put the current call on hold"
            ),

            CommandTemplate(
                name="transfer_call",
                pattern=r"(?:transfer|forward|redirect)\s+(?:call)?\s+(?:to|with|for)\s+(\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}|\d{7,15})",
                command_type="call_control",
                priority=CommandPriority.HIGH,
                required_params=["target"],
                optional_params=["conference"],
                validation_rules={
                    "target_validation": True,
                    "conference_validation": True
                },
                action_mapping={
                    "jarvis_cli": "call --transfer {target}",
                    "fastapi": "/call/transfer",
                    "websocket": "transfer_call"
                },
                help_text="Transfer the current call to another number"
            ),
        ]

        # System status commands
        status_templates = [
            CommandTemplate(
                name="system_status",
                pattern=r"(?:system|status|call|connection)\s+(?:status|state|health|check|info)",
                command_type="system",
                priority=CommandPriority.MEDIUM,
                required_params=[],
                optional_params=["detailed"],
                validation_rules={
                    "detailed_validation": ["true", "false", "full"],
                    "status_source_validation": ["jarvis", "android", "api"]
                },
                action_mapping={
                    "jarvis_cli": "status",
                    "fastapi": "/status",
                    "websocket": "system_status"
                },
                help_text="Check system status and call state"
            ),

            CommandTemplate(
                name="device_status",
                pattern=r"(?:device|phone|android|sim)\s+(?:status|state|health|check)",
                command_type="system",
                priority=CommandPriority.MEDIUM,
                required_params=[],
                optional_params=["sim_specific"],
                validation_rules={
                    "sim_specific_validation": ["SIM1", "SIM2"],
                    "device_type_validation": ["android", "usb", "bluetooth"]
                },
                action_mapping={
                    "jarvis_cli": "status",
                    "fastapi": "/status",
                    "websocket": "device_status"
                },
                help_text="Check device and SIM status"
            ),
        ]

        # Help and information commands
        help_templates = [
            CommandTemplate(
                name="help_commands",
                pattern=r"(?:help|assist|guide|info|support)\s*(?:about|for|with)?\s*(?:commands|features?|voice)?",
                command_type="help",
                priority=CommandPriority.LOW,
                required_params=[],
                optional_params=["category"],
                validation_rules={
                    "category_validation": ["telephony", "voice", "system", "all"],
                    "language_validation": ["en", "es", "fr", "de"]
                },
                action_mapping={
                    "jarvis_cli": "help",
                    "fastapi": "/help",
                    "websocket": "help_commands"
                },
                help_text="Get help information about available commands"
            ),

            CommandTemplate(
                name="command_examples",
                pattern=r"(?:examples|sample|demo|how\s+to|tutorial)\s*(?:of|for)?\s*(?:commands|voice|voice\s+commands?)",
                command_type="help",
                priority=CommandPriority.LOW,
                required_params=[],
                optional_params=["topic"],
                validation_rules={
                    "topic_validation": ["call", "balance", "system", "all"],
                    "language_validation": ["en", "es", "fr", "de"]
                },
                action_mapping={
                    "jarvis_cli": "help examples",
                    "fastapi": "/examples",
                    "websocket": "command_examples"
                },
                help_text="Get examples of voice commands"
            ),
        ]

        # Exit and control commands
        exit_templates = [
            CommandTemplate(
                name="exit_jarvis",
                pattern=r"(?:exit|quit|stop|end|terminate|shutdown|off|goodbye|bye)",
                command_type="control",
                priority=CommandPriority.IMMEDIATE,
                required_params=[],
                optional_params=["confirmation"],
                validation_rules={
                    "confirmation_required": True,
                    "exit_timeout": 10
                },
                action_mapping={
                    "jarvis_cli": "exit",
                    "fastapi": "/exit",
                    "websocket": "exit"
                },
                help_text="Exit Jarvis or stop voice interface"
            ),

            CommandTemplate(
                name="pause_voice",
                pattern=r"(?:pause|stop listening|silence|quiet|mute)\s*(?:voice|listening)?",
                command_type="control",
                priority=CommandPriority.HIGH,
                required_params=[],
                optional_params=["duration"],
                validation_rules={
                    "duration_validation": True,
                    "pause_only": True
                },
                action_mapping={
                    "jarvis_cli": "voice pause",
                    "fastapi": "/voice/pause",
                    "websocket": "pause_voice"
                },
                help_text="Pause voice recognition temporarily"
            ),
        ]

        # Combine all templates
        all_templates = call_templates + balance_templates + call_management_templates + status_templates + help_templates + exit_templates

        # Register all templates
        for template in all_templates:
            self.command_templates[template.name] = template

    def register_command_handler(self, command_type: str, handler: Callable):
        """Register a handler for a specific command type"""
        self.command_handlers[command_type] = handler
        self.logger.info(f"Registered handler for command type: {command_type}")

    def process_voice_input(self, raw_text: str, confidence: float = 0.85,
                          context: Dict[str, Any] = None) -> Optional[VoiceCommand]:
        """Process raw voice input and extract structured command"""
        if confidence < self.config["voice_confidence_threshold"]:
            self.logger.warning(f"Voice confidence below threshold: {confidence}")
            return None

        # Check for duplicate commands
        if self._is_duplicate_command(raw_text):
            self.logger.info(f"Duplicate command detected (within {self.config['duplicate_command_window']}s): {raw_text}")
            return None

        # Extract and match command templates
        command = self._match_command_templates(raw_text, context)
        if not command:
            self.logger.warning(f"No command template matched for: {raw_text}")
            return None

        # Add to history
        self.command_history.append(command)

        # Keep history within limits
        if len(self.command_history) > self.config["max_command_history"]:
            self.command_history = self.command_history[-self.config["max_command_history"]//2:]

        # Update statistics
        self._update_stats(command)

        self.logger.info(f"Processed voice command: {command.parsed_command} (confidence: {confidence})")
        return command

    def _match_command_templates(self, raw_text: str, context: Dict[str, Any] = None) -> Optional[VoiceCommand]:
        """Match voice text against command templates"""
        if not context:
            context = {}

        best_match = None
        highest_confidence = 0.0

        for template_name, template in self.command_templates.items():
            # Calculate confidence score
            confidence = self._calculate_template_confidence(raw_text, template)

            if confidence > highest_confidence:
                highest_confidence = confidence
                best_match = template

        if not best_match:
            return None

        # Extract parameters from matched template
        parameters = self._extract_parameters_from_text(raw_text, best_match)

        # Validate parameters
        if not self._validate_parameters(parameters, best_match):
            self.logger.warning(f"Parameter validation failed for template: {best_match.name}")
            return None

        # Create VoiceCommand object
        command_id = f"cmd_{int(time.time())}_{len(self.command_history)}"

        return VoiceCommand(
            id=command_id,
            raw_text=raw_text,
            parsed_command=best_match.name,
            confidence=highest_confidence,
            timestamp=datetime.now(),
            priority=best_match.priority,
            status=CommandStatus.PENDING,
            parameters=parameters,
            context=context,
            source="voice"
        )

    def _calculate_template_confidence(self, text: str, template: CommandTemplate) -> float:
        """Calculate confidence score for template matching"""
        confidence = 0.0
        text_lower = text.lower()

        # Check pattern matching
        if re.search(template.pattern, text_lower, re.IGNORECASE):
            confidence += 0.7
        else:
            return 0.0

        # Check for exact keyword matches
        keywords = self._extract_keywords_from_pattern(template.pattern)
        for keyword in keywords:
            if keyword.lower() in text_lower:
                confidence += 0.1

        # Adjust based on text length (avoid very short matches)
        if len(text.split()) < 3:
            confidence *= 0.8

        return min(confidence, 1.0)

    def _extract_keywords_from_pattern(self, pattern: str) -> List[str]:
        """Extract keywords from command pattern"""
        keywords = []

        # Common voice command keywords
        common_keywords = [
            'call', 'call', 'call', 'call', 'call', 'call', 'call'
        ]

        return common_keywords

    def _extract_parameters_from_text(self, text: str, template: CommandTemplate) -> Dict[str, Any]:
        """Extract parameters from text using template pattern"""
        parameters = {}
        text_lower = text.lower()

        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}|\d{7,15})'
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            parameters['target'] = phone_matches[0]

        # Extract SIM numbers
        sim_pattern = r'(?:sim\s*(\d+))'
        sim_matches = re.findall(sim_pattern, text_lower)
        if sim_matches:
            parameters['sim'] = f"SIM{sim_matches[0]}"

        # Extract numbers for SIM2
        if 'sim2' in text_lower:
            parameters['sim'] = 'SIM2'

        # Handle specific parameter extractions based on template
        if template.name == 'place_call':
            if 'target' not in parameters:
                # Try to extract from text without 'call' prefix
                remaining_text = re.sub(r'call\s+(?:number\s+)?', '', text_lower)
                if remaining_text:
                    parameters['target'] = remaining_text.strip()

        elif template.name == 'check_balance':
            if 'sim' not in parameters:
                parameters['sim'] = 'SIM1'  # Default SIM

        return parameters

    def _validate_parameters(self, parameters: Dict[str, Any], template: CommandTemplate) -> bool:
        """Validate extracted parameters against template requirements"""
        if self.config["enable_command_validation"]:
            # Check required parameters
            for required_param in template.required_params:
                if required_param not in parameters:
                    self.logger.warning(f"Missing required parameter: {required_param}")
                    return False

            # Check parameter values against validation rules
            if "sim_validation" in template.validation_rules:
                valid_sims = template.validation_rules["sim_validation"]
                if 'sim' in parameters and parameters['sim'] not in valid_sims:
                    self.logger.warning(f"Invalid SIM value: {parameters['sim']}")
                    return False

            if "phone_number_validation" in template.validation_rules:
                phone_pattern = r'(\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}|\d{7,15})'
                if 'target' in parameters and not re.search(phone_pattern, parameters['target']):
                    self.logger.warning(f"Invalid phone number format: {parameters['target']}")
                    return False

        return True

    def _is_duplicate_command(self, text: str) -> bool:
        """Check if command is a duplicate of recent commands"""
        current_time = time.time()
        duplicate_window = self.config["duplicate_command_window"]

        for command in self.command_history[-10:]:  # Check last 10 commands
            time_diff = (current_time - command.timestamp.timestamp()) if hasattr(command.timestamp, 'timestamp') else 0
            if time_diff < duplicate_window:
                # Simple text comparison for now
                if command.raw_text.lower() == text.lower():
                    return True

        return False

    def execute_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute a processed voice command"""
        if command.status != CommandStatus.PENDING:
            return {"status": "error", "message": "Command already processed"}

        command.status = CommandStatus.PROCESSING
        start_time = time.time()

        try:
            # Check if we have a handler for this command type
            if command.parsed_command in self.command_handlers:
                result = self.command_handlers[command.parsed_command](command)
            else:
                # Use action mapping to construct command for different interfaces
                result = self._execute_via_action_mapping(command)

            # Update command status
            command.status = CommandStatus.COMPLETED
            command.processing_time = time.time() - start_time
            command.result = result

            self.logger.info(f"Command executed successfully: {command.parsed_command}")
            return result

        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            command.processing_time = time.time() - start_time

            self.logger.error(f"Command execution failed: {e}")
            return {"status": "error", "message": str(e)}

    def _execute_via_action_mapping(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute command using action mapping"""
        template = self.command_templates.get(command.parsed_command)
        if not template:
            return {"status": "error", "message": f"Unknown command: {command.parsed_command}"}

        # Get action mapping based on command type
        action_mapping = template.action_mapping

        # Try different execution interfaces in order of preference
        interfaces = ['jarvis_cli', 'fastapi', 'websocket']

        for interface in interfaces:
            if interface in action_mapping:
                action = action_mapping[interface]

                # Format action with command parameters
                formatted_action = self._format_action(action, command.parameters)

                # Execute action
                result = self._execute_action(formatted_action, interface)
                if result["status"] != "error":
                    return result

        return {"status": "error", "message": f"No suitable interface found for command: {command.parsed_command}"}

    def _format_action(self, action: str, parameters: Dict[str, Any]) -> str:
        """Format action string with parameters"""
        formatted = action

        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            if placeholder in formatted:
                formatted = formatted.replace(placeholder, str(value))

        return formatted

    def _execute_action(self, action: str, interface: str) -> Dict[str, Any]:
        """Execute action on specified interface"""
        if interface == 'jarvis_cli':
            return self._execute_jarvis_cli(action)
        elif interface == 'fastapi':
            return self._execute_fastapi(action)
        elif interface == 'websocket':
            return self._execute_websocket(action)
        else:
            return {"status": "error", "message": f"Unknown interface: {interface}"}

    def _execute_jarvis_cli(self, action: str) -> Dict[str, Any]:
        """Execute action via Jarvis CLI"""
        import subprocess

        try:
            result = subprocess.run(
                ["python", "jarvis_cli.py"] + action.split(),
                capture_output=True,
                text=True,
                timeout=self.config["command_timeout"],
                cwd=r"C:\Users\Free user\Jarvis"
            )

            if result.returncode == 0:
                return {"status": "success", "output": result.stdout.strip()}
            else:
                return {"status": "error", "message": result.stderr.strip()}

        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_fastapi(self, action: str) -> Dict[str, Any]:
        """Execute action via FastAPI"""
        try:
            # Parse action to determine endpoint
            # This is a simplified implementation - would need proper parsing
            base_url = "http://localhost:8000"

            # Map action to endpoint
            endpoint_mapping = {
                "call": "/call",
                "balance": "/ussd/balance",
                "hangup": "/calls/hangup",
                "status": "/status"
            }

            # For now, return a placeholder
            return {"status": "pending", "message": f"FastAPI action queued: {action}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _execute_websocket(self, action: str) -> Dict[str, Any]:
        """Execute action via WebSocket"""
        try:
            # Placeholder for WebSocket implementation
            return {"status": "pending", "message": f"WebSocket action queued: {action}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _update_stats(self, command: VoiceCommand):
        """Update command processing statistics"""
        self.stats['total_commands_processed'] += 1

        if command.status == CommandStatus.COMPLETED:
            self.stats['successful_commands'] += 1
        elif command.status == CommandStatus.FAILED:
            self.stats['failed_commands'] += 1

        # Update average processing time
        if command.processing_time:
            total_time = self.stats['average_processing_time'] * (self.stats['total_commands_processed'] - 1)
            total_time += command.processing_time
            self.stats['average_processing_time'] = total_time / self.stats['total_commands_processed']

        # Update command distribution
        if command.parsed_command not in self.stats['command_distribution']:
            self.stats['command_distribution'][command.parsed_command] = 0
        self.stats['command_distribution'][command.parsed_command] += 1

    def get_command_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get command history with optional limit"""
        history = []

        for command in self.command_history:
            history.append({
                'id': command.id,
                'raw_text': command.raw_text,
                'parsed_command': command.parsed_command,
                'confidence': command.confidence,
                'timestamp': command.timestamp.isoformat(),
                'status': command.status.value,
                'parameters': command.parameters,
                'result': command.result
            })

        if limit:
            history = history[-limit:]

        return history

    def get_stats(self) -> Dict[str, Any]:
        """Get command processing statistics"""
        return self.stats.copy()

    def clear_command_history(self):
        """Clear command history"""
        self.command_history = []
        self.stats = {
            'total_commands_processed': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'average_processing_time': 0.0,
            'command_distribution': {}
        }
        self.logger.info("Command history cleared")

    def get_suggestions(self, partial_text: str, limit: int = 5) -> List[str]:
        """Get command suggestions based on partial text"""
        suggestions = []

        for template_name in self.command_templates.keys():
            if partial_text.lower() in template_name.lower():
                suggestions.append(template_name)
                if len(suggestions) >= limit:
                    break

        return suggestions

    def add_custom_command(self, name: str, template: CommandTemplate):
        """Add a custom command template"""
        self.command_templates[name] = template
        self.logger.info(f"Added custom command template: {name}")

def main():
    """Example usage of Jarvis Voice Command Processor"""
    print("Initializing Jarvis Voice Command Processor...")

    # Create voice command processor
    processor = VoiceCommandProcessor()

    # Test command processing
    test_commands = [
        "Call 0922233398",
        "Check balance for SIM1",
        "Hang up call",
        "System status"
    ]

    print("\nTesting voice command processing...")
    for text in test_commands:
        print(f"\nProcessing: '{text}'")

        # Process voice input
        command = processor.process_voice_input(text, confidence=0.85)

        if command:
            print(f"  Parsed: {command.parsed_command}")
            print(f"  Parameters: {command.parameters}")
            print(f"  Confidence: {command.confidence}")

            # Execute command
            result = processor.execute_command(command)
            print(f"  Result: {result}")
        else:
            print("  Failed to parse command")

    # Print statistics
    print("\n=== Command Statistics ===")
    stats = processor.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n=== Command History ===")
    history = processor.get_command_history(10)
    for cmd in history:
        print(f"  {cmd['timestamp']}: {cmd['parsed_command']} -> {cmd['status']}")

if __name__ == "__main__":
    main()