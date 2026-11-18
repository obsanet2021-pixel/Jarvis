"""
Jarvis Voice Interface
AI Assistant Voice Recognition and Synthesis Module

This module provides voice capabilities for Jarvis, including:
- Speech-to-text (STT) conversion
- Text-to-speech (TTS) synthesis
- Voice command processing
- Audio logging and monitoring
- Voice activity detection
"""

import asyncio
import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
import queue
import sys
import platform

# Try to import voice libraries with graceful fallbacks
STT_AVAILABLE = False
TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    print("Warning: speech_recognition not available. Install with: pip install SpeechRecognition")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("Warning: pyttsx3 not available. Install with: pip install pyttsx3")

# Try Fish Audio if available
try:
    import fishaudio as _fa_mod  # installed package is fishaudio; fish_audio_sdk is the dist-info compat name
    FISH_AUDIO_AVAILABLE = True
except ImportError:
    FISH_AUDIO_AVAILABLE = False
    print("Warning: Fish Audio SDK not available")

# Global instances
speech_recognizer = None
tts_engine = None
fish_audio_client = None

class VoiceEngine(Enum):
    SYSTEM = "system"
    FISH_AUDIO = "fish_audio"
    ECHO_VOICE = "echo_voice"

class VoiceCommand(Enum):
    CALL = "call"
    BALANCE = "balance"
    HANGUP = "hangup"
    STATUS = "status"
    HELP = "help"
    EXIT = "exit"
    UNKNOWN = "unknown"

@dataclass
class VoiceCommandResult:
    command: VoiceCommand
    confidence: float
    text: str
    parameters: Dict[str, Any]
    audio_data: bytes = None

class JarvisVoiceInterface:
    """Main voice interface class for Jarvis AI assistant"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.current_engine = VoiceEngine.SYSTEM
        self.is_listening = False
        self.is_speaking = False
        self._listener_thread: Optional[threading.Thread] = None
        self._listen_stop = threading.Event()
        self.command_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.callbacks = {}

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize voice engines
        self._init_speech_recognition()
        self._init_text_to_speech()
        self._init_fish_audio()

        # Command mapping for voice commands
        self.command_mapping = {
            VoiceCommand.CALL: self._handle_call_command,
            VoiceCommand.BALANCE: self._handle_balance_command,
            VoiceCommand.HANGUP: self._handle_hangup_command,
            VoiceCommand.STATUS: self._handle_status_command,
            VoiceCommand.HELP: self._handle_help_command,
            VoiceCommand.EXIT: self._handle_exit_command,
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load voice interface configuration"""
        default_config = {
            "stt": {
                "engine": "speech_recognition",
                "language": "en-US",
                "phrase_time_limit": 5,
                "energy_threshold": 300,
                "dynamic_energy_threshold": True,
                "pause_threshold": 0.8,
                "phrase_threshold": 0.3
            },
            "tts": {
                "engine": "pyttsx3",
                "voice_id": 0,
                "rate": 150,
                "volume": 0.8,
                "language": "en"
            },
            "fish_audio": {
                "enabled": False,
                "api_key": os.getenv("FISH_AUDIO_API_KEY"),
                "model_id": "your-model-id",
                "sample_rate": 22050
            },
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "format": "wav",
                "chunk_size": 1024,
                "max_record_length": 10
            },
            "commands": {
                "call_keywords": ["call", "phone", "dial", "contact"],
                "balance_keywords": ["balance", "credit", "charge", "bill"],
                "hangup_keywords": ["hangup", "end", "stop", "cancel"],
                "status_keywords": ["status", "state", "check", "current"],
                "help_keywords": ["help", "assist", "guide", "support"],
                "exit_keywords": ["exit", "quit", "stop", "goodbye", "off"]
            },
            "vad": {
                "silence_threshold": 300,
                "silence_duration": 1.0,
                "voice_activity_timeout": 5.0
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def _init_speech_recognition(self):
        """Initialize speech recognition engine"""
        global speech_recognizer
        if STT_AVAILABLE:
            speech_recognizer = sr.Recognizer()
            speech_recognizer.energy_threshold = self.config["stt"]["energy_threshold"]
            speech_recognizer.dynamic_energy_threshold = self.config["stt"]["dynamic_energy_threshold"]
            speech_recognizer.pause_threshold = self.config["stt"]["pause_threshold"]
            speech_recognizer.phrase_threshold = self.config["stt"]["phrase_threshold"]
            self.logger.info("Speech recognition engine initialized")

    def _init_text_to_speech(self):
        """Initialize text-to-speech engine"""
        global tts_engine
        if TTS_AVAILABLE:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', self.config["tts"]["rate"])
            tts_engine.setProperty('volume', self.config["tts"]["volume"])

            # Set voice
            voices = tts_engine.getProperty('voices')
            if voices:
                tts_engine.setProperty('voice', voices[self.config["tts"]["voice_id"]].id)

            self.logger.info("Text-to-speech engine initialized")

    def _init_fish_audio(self):
        """Initialize Fish Audio engine if available"""
        global fish_audio_client
        if not FISH_AUDIO_AVAILABLE:
            return
        api_key = self.config["fish_audio"]["api_key"] or os.getenv("FISH_API_KEY") or os.getenv("FISH_AUDIO_API_KEY")
        if not api_key:
            self.logger.info("Fish Audio disabled — no API key configured")
            return
        try:
            from fishaudio import FishAudio
            fish_audio_client = FishAudio(api_key=api_key)
            self.logger.info("Fish Audio engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Fish Audio: {e}")
            fish_audio_client = None

    def start_listening(self, callback: Callable[[VoiceCommandResult], None] = None):
        """Start voice recognition and processing"""
        if not STT_AVAILABLE:
            self.logger.error("Speech recognition not available. Please install: pip install SpeechRecognition")
            return False

        if self.is_listening and self._listener_thread and self._listener_thread.is_alive():
            self.logger.warning("Listener already active")
            return True

        self.is_listening = True
        self._listen_stop.clear()
        self.logger.info("Starting voice recognition...")

        if callback:
            self.callbacks['voice_result'] = callback

        # Start listening thread
        self._listener_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        self._listener_thread.start()

        return True

    def _listen_for_commands(self):
        """Continuous voice listening thread"""
        while not self._listen_stop.is_set():
            try:
                with sr.Microphone() as source:
                    self.logger.info("Adjusting for ambient noise...")
                    speech_recognizer.adjust_for_ambient_noise(source, duration=1)

                    self.logger.info("Listening for voice commands...")
                    audio = speech_recognizer.listen(
                        source,
                        timeout=self.config["stt"]["phrase_time_limit"],
                        phrase_time_limit=self.config["stt"]["phrase_time_limit"]
                    )

                    if audio:
                        # Process the audio
                        self._process_audio(audio)

            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                if self.is_listening:
                    self.logger.error(f"Error in voice recognition: {e}")
                    time.sleep(0.5)

    def _process_audio(self, audio):
        """Process captured audio and extract commands"""
        try:
            if not STT_AVAILABLE:
                return

            # Convert audio to text using speech recognition
            text = speech_recognizer.recognize_google(
                audio,
                language=self.config["stt"]["language"]
            )

            self.logger.info(f"Recognized: {text}")

            # Extract voice command
            result = self._extract_command_from_text(text)

            if result:
                # Emit command result
                if 'voice_result' in self.callbacks:
                    self.callbacks['voice_result'](result)

        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition error: {e}")
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")

    def _extract_command_from_text(self, text: str) -> Optional[VoiceCommandResult]:
        """Extract voice command from recognized text"""
        text_lower = text.lower()

        # Check for each command type
        for command in VoiceCommand:
            if command == VoiceCommand.UNKNOWN:
                continue

            # Get keywords for this command
            keywords_map = {
                VoiceCommand.CALL: self.config["commands"]["call_keywords"],
                VoiceCommand.BALANCE: self.config["commands"]["balance_keywords"],
                VoiceCommand.HANGUP: self.config["commands"]["hangup_keywords"],
                VoiceCommand.STATUS: self.config["commands"]["status_keywords"],
                VoiceCommand.HELP: self.config["commands"]["help_keywords"],
                VoiceCommand.EXIT: self.config["commands"]["exit_keywords"]
            }

            keywords = keywords_map.get(command, [])

            for keyword in keywords:
                if keyword in text_lower:
                    # Extract parameters from text
                    params = self._extract_parameters_from_text(text, command)

                    return VoiceCommandResult(
                        command=command,
                        confidence=0.85,  # Default confidence for keyword matching
                        text=text,
                        parameters=params
                    )

        # No command found
        return VoiceCommandResult(
            command=VoiceCommand.UNKNOWN,
            confidence=0.0,
            text=text,
            parameters={}
        )

    def _extract_parameters_from_text(self, text: str, command: VoiceCommand) -> Dict[str, Any]:
        """Extract parameters from voice command text"""
        params = {}
        text_lower = text.lower()

        if command == VoiceCommand.CALL:
            # Try to extract phone number from text
            import re
            phone_pattern = r'\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}'
            match = re.search(phone_pattern, text)
            if match:
                params['target'] = match.group(0)

        elif command == VoiceCommand.BALANCE:
            # Extract SIM preference if mentioned
            if 'sim1' in text_lower:
                params['sim'] = 'SIM1'
            elif 'sim2' in text_lower:
                params['sim'] = 'SIM2'

        elif command == VoiceCommand.HANGUP:
            params['confirm'] = True  # Default confirmation for safety

        return params

    def speak(self, text: str, engine: VoiceEngine = None) -> bool:
        """Convert text to speech and play it"""
        if not TTS_AVAILABLE:
            self.logger.error("Text-to-speech not available. Please install: pip install pyttsx3")
            return False

        if self.is_speaking:
            self.logger.warning("Already speaking, cannot start new speech")
            return False

        self.is_speaking = True
        self.logger.info(f"Speaking: {text}")

        try:
            # Use specified engine or default
            voice_engine = engine or self.current_engine

            if voice_engine == VoiceEngine.FISH_AUDIO and FISH_AUDIO_AVAILABLE and fish_audio_client:
                # Use Fish Audio for TTS
                self._speak_with_fish_audio(text)
            else:
                # Use system TTS
                tts_engine.say(text)
                tts_engine.runAndWait()

            return True

        except Exception as e:
            self.logger.error(f"Error speaking: {e}")
            return False
        finally:
            self.is_speaking = False

    def _speak_with_fish_audio(self, text: str):
        """Use Fish Audio for text-to-speech via pyaudio playback."""
        global fish_audio_client
        if not fish_audio_client:
            return
        try:
            import pyaudio
            audio_bytes = fish_audio_client.tts.convert(text=text)
            if not audio_bytes:
                return
            # Decode MP3/OGG → WAV bytes then play via pyaudio (no external deps).
            # Shortcut: uses ffmpeg via subprocess; falls back if unavailable.
            import subprocess, tempfile, os
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            try:
                tmp.write(audio_bytes)
                tmp.close()
                wav_out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                wav_out.close()
                rc = subprocess.run(
                    ["ffmpeg", "-y", "-i", tmp.name, "-acodec", "pcm_s16le",
                     "-ar", "24000", "-ac", "1", wav_out.name],
                    capture_output=True, timeout=30
                )
                if rc.returncode != 0:
                    # Fallback: raw mp3 stream (pyaudio can't decode mp3 natively).
                    # Use the raw bytes and hope for the best, or just skip playback.
                    os.unlink(wav_out.name)
                    self.logger.warning("FFmpeg unavailable for Fish Audio playback — skipping TTS")
                    return
                with open(wav_out.name, "rb") as f:
                    wav_data = f.read()
            finally:
                os.unlink(tmp.name)
                try:
                    os.unlink(wav_out.name)
                except OSError:
                    pass
            # Parse minimal WAV header to extract PCM data.
            if wav_data[:4] != b'RIFF' or wav_data[8:12] != b'WAVE':
                return
            fmt_idx = wav_data.find(b'fmt ')
            if fmt_idx < 0:
                return
            data_idx = wav_data.find(b'data')
            if data_idx < 0:
                return
            chunk_size = int.from_bytes(wav_data[data_idx + 4:data_idx + 8], 'little')
            pcm_start = data_idx + 8
            pcm = wav_data[pcm_start:pcm_start + chunk_size]
            rate = int.from_bytes(wav_data[fmt_idx + 8:fmt_idx + 12], 'little')
            channels = int.from_bytes(wav_data[fmt_idx + 12:fmt_idx + 14], 'little')
            bits = int.from_bytes(wav_data[fmt_idx + 14:fmt_idx + 16], 'little')
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pa.get_format_from_width(bits // 8),
                             channels=channels, rate=rate, output=True)
            stream.write(pcm)
            stream.stop_stream()
            stream.close()
            pa.terminate()
        except Exception as e:
            self.logger.error(f"Fish Audio speak failed: {e}")

    def register_callback(self, event: str, callback: Callable):
        """Register a callback for voice events"""
        self.callbacks[event] = callback
        self.logger.info(f"Registered callback for event: {event}")

    def unregister_callback(self, event: str):
        """Unregister a callback"""
        if event in self.callbacks:
            del self.callbacks[event]
        self.logger.info(f"Unregistered callback for event: {event}")

    def _handle_call_command(self, result: VoiceCommandResult):
        """Handle call voice command"""
        self.logger.info(f"Handling call command: {result.text}")

        # Extract target from parameters or result text
        target = result.parameters.get('target')
        if not target:
            # Try to extract from text
            import re
            phone_pattern = r'\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}'
            match = re.search(phone_pattern, result.text)
            if match:
                target = match.group(0)

        if target:
            self.speak(f"Initiating call to {target}.")
            # TODO: Send call command to Jarvis system
            self.logger.info(f"Call command would be sent to: {target}")
        else:
            self.speak("I need a phone number to call. Please specify the number.")

    def _handle_balance_command(self, result: VoiceCommandResult):
        """Handle balance check voice command"""
        self.logger.info(f"Handling balance command: {result.text}")

        sim = result.parameters.get('sim', 'SIM1')
        self.speak(f"Checking balance for {sim}.")
        # TODO: Send balance check command to Jarvis system
        self.logger.info(f"Balance command would be sent for: {sim}")

    def _handle_hangup_command(self, result: VoiceCommandResult):
        """Handle hangup voice command"""
        self.logger.info(f"Handling hangup command: {result.text}")

        if result.parameters.get('confirm', False):
            self.speak("Terminating call.")
            # TODO: Send hangup command to Jarvis system
            self.logger.info("Hangup command would be sent")
        else:
            self.speak("Do you want to end the call? Please confirm.")

    def _handle_status_command(self, result: VoiceCommandResult):
        """Handle status voice command"""
        self.logger.info(f"Handling status command: {result.text}")
        self.speak("Checking system status.")
        # TODO: Send status check command to Jarvis system
        self.logger.info("Status command would be sent")

    def _handle_help_command(self, result: VoiceCommandResult):
        """Handle help voice command"""
        self.logger.info(f"Handling help command: {result.text}")
        help_text = (
            "Available voice commands: "
            "call <number> to place a phone call, "
            "balance to check account balance, "
            "hangup to end a call, "
            "status to check system status, "
            "help for assistance, "
            "exit to quit"
        )
        self.speak(help_text)

    def _handle_exit_command(self, result: VoiceCommandResult):
        """Handle exit voice command"""
        self.logger.info(f"Handling exit command: {result.text}")
        self.speak("Goodbye! Exiting Jarvis.")
        self.is_listening = False
        # TODO: Send exit command to Jarvis system

    def stop_listening(self):
        """Stop voice recognition"""
        self.is_listening = False
        self._listen_stop.set()
        if self._listener_thread:
            self._listener_thread.join(timeout=2.0)
        self.logger.info("Voice recognition stopped")

    def set_voice_engine(self, engine: VoiceEngine):
        """Set the voice engine to use"""
        self.current_engine = engine
        self.logger.info(f"Voice engine set to: {engine.value}")

    def get_status(self) -> Dict[str, Any]:
        """Get current voice interface status"""
        return {
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "current_engine": self.current_engine.value,
            "stt_available": STT_AVAILABLE,
            "tts_available": TTS_AVAILABLE,
            "fish_audio_available": FISH_AUDIO_AVAILABLE,
            "config": self.config
        }

def main():
    """Example usage of Jarvis Voice Interface"""
    print("Initializing Jarvis Voice Interface...")

    # Create voice interface
    voice = JarvisVoiceInterface()

    # Print status
    status = voice.get_status()
    print(f"Voice Interface Status: {json.dumps(status, indent=2)}")

    # Define callback for voice commands
    def on_voice_command(result):
        print(f"\n=== Voice Command Detected ===")
        print(f"Command: {result.command.value}")
        print(f"Text: {result.text}")
        print(f"Confidence: {result.confidence}")
        print(f"Parameters: {result.parameters}")
        print(f"====================\n")

    # Register callback
    voice.register_callback('voice_result', on_voice_command)

    # Start listening for voice commands
    if voice.start_listening():
        print("\n🎤 Jarvis Voice Interface is now active!")
        print("Speak voice commands like:")
        print("  - 'Call 0922233398'")
        print("  - 'Check balance'")
        print("  - 'Hang up'")
        print("  - 'Status'")
        print("  - 'Help'")
        print("  - 'Exit'")
        print("\nPress Ctrl+C to stop...")

        try:
            # Keep the program running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping voice interface...")
            voice.stop_listening()
    else:
        print("Failed to start voice recognition")

if __name__ == "__main__":
    main()