"""
JARVIS-specific fact extractor for conversation turns.

Extracts durable facts about phone numbers, SIM details, USSD codes,
and user preferences from JARVIS interactions.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, List, Optional

from openjarvis.memory.extractor import FactExtractor

logger = logging.getLogger(__name__)

# JARVIS-specific extraction prompt
_JARVIS_SYSTEM_PROMPT = (
    "You extract durable, long-term facts about the user from a single "
    "conversation exchange. Focus on JARVIS-specific information:\n"
    "- Phone numbers and their labels\n"
    "- SIM card details (SIM1, SIM2) with networks and USSD codes\n"
    "- User preferences for calling, balance checking, or voice settings\n"
    "- Ongoing projects or tasks mentioned\n"
    "- Constraints or rules the user has set\n\n"
    "Ignore one-off task details, small talk, and system messages.\n"
    "Respond with ONLY a JSON array of short fact strings (each under 200 "
    "characters). If there is nothing worth remembering, respond with []."
)


class JARVISFactExtractor(FactExtractor):
    """Extract JARVIS-specific facts from conversation turns."""

    def __init__(
        self,
        engine: Any,
        model: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 512,
        max_facts_per_turn: int = 10,
        max_fact_chars: int = 200,
        system_prompt: Optional[str] = None,
    ) -> None:
        super().__init__(
            engine,
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            max_facts_per_turn=max_facts_per_turn,
            max_fact_chars=max_fact_chars,
            system_prompt=system_prompt or _JARVIS_SYSTEM_PROMPT,
        )

    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text using pattern matching."""
        # Match Ethiopian phone numbers
        patterns = [
            r"\+2519\d{8}",  # Ethio Telecom mobile
            r"\+2517\d{8}",  # Safaricom mobile
            r"09\d{8}",      # Ethio Telecom local
            r"07\d{8}",      # Safaricom local
        ]
        numbers = []
        for pattern in patterns:
            numbers.extend(re.findall(pattern, text))
        return list(set(numbers))

    def extract_ussd_codes(self, text: str) -> List[str]:
        """Extract USSD codes from text."""
        pattern = r"\*[0-9]{1,15}#"
        return list(set(re.findall(pattern, text)))

    def extract_sim_info(self, text: str) -> List[dict]:
        """Extract SIM configuration information."""
        sim_info = []
        # Match patterns like "SIM1: +2519... on Ethio Telecom with USSD *804#"
        pattern = r"(SIM[12]):\s*(\+?\d{10,15})\s+on\s+(\w[\w\s]+?)\s+with\s+(\*[0-9]{1,15}#)"
        for match in re.finditer(pattern, text, re.IGNORECASE):
            sim_info.append(
                {
                    "sim_key": match.group(1),
                    "phone_number": match.group(2),
                    "network": match.group(3).strip(),
                    "ussd_code": match.group(4),
                }
            )
        return sim_info


__all__ = ["JARVISFactExtractor"]