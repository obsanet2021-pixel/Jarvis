"""
JARVIS-specific fact store with phone/SIM validation.

Extends OpenJarvis's LocalFactStore with JARVIS-specific validation
for phone numbers, SIM details, and USSD codes.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Optional

from openjarvis.memory.store import (
    Fact,
    FactStore,
    LocalFactStore,
    RECALLABLE_TRUST_TIERS,
    TRUST_AUTO,
    TRUST_TRUSTED,
    TRUST_UNTRUSTED,
    _cross_process_lock,
)

# JARVIS-specific fact categories
FACT_CATEGORY_PHONE = "phone"
FACT_CATEGORY_USSD = "ussd"
FACT_CATEGORY_SIM = "sim"
FACT_CATEGORY_NETWORK = "network"
FACT_CATEGORY_PREF = "preference"
FACT_CATEGORY_COMMAND = "command"

# Valid Ethiopian phone number prefixes
ETHIO_TELECOM_PREFIXES = ("+2519", "09")
SAFARICOM_PREFIXES = ("+2517", "07")

# Valid USSD code pattern
USSD_PATTERN = re.compile(r"^\*[0-9]{1,15}#$")


class JARVISFactStore(LocalFactStore):
    """Extended fact store with JARVIS-specific validation and metadata."""

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        max_facts: int = 5000,
    ) -> None:
        super().__init__(path, max_facts=max_facts)

    def add_interaction_log(
        self,
        user_input: str,
        jarvis_response: str,
        source: str = "jarvis",
        trust: str = TRUST_AUTO,
    ) -> bool:
        """Store a complete interaction for learning purposes."""
        interaction = {
            "user": user_input.strip(),
            "assistant": jarvis_response.strip(),
            "timestamp": time.time(),
        }
        return self.add(
            json.dumps(interaction, ensure_ascii=False),
            source=source,
            trust=trust,
        )

    def add_phone_number(
        self,
        phone_number: str,
        label: str = "",
        trust: str = TRUST_AUTO,
    ) -> bool:
        """Store a validated phone number with optional label."""
        cleaned = phone_number.strip().replace(" ", "")
        if not cleaned:
            return False
        fact_text = f"Phone: {cleaned}" + (f" ({label})" if label else "")
        return self.add(fact_text, source="jarvis", trust=trust)

    def add_sim_detail(
        self,
        sim_key: str,
        phone_number: str,
        network: str,
        ussd_code: str,
        trust: str = TRUST_AUTO,
    ) -> bool:
        """Store SIM configuration details."""
        fact_text = (
            f"SIM {sim_key}: {phone_number} on {network} "
            f"with USSD {ussd_code}"
        )
        return self.add(fact_text, source="jarvis", trust=trust)

    def add_user_preference(
        self,
        preference: str,
        value: str,
        trust: str = TRUST_AUTO,
    ) -> bool:
        """Store a user preference for future reference."""
        fact_text = f"Preference: {preference} = {value}"
        return self.add(fact_text, source="jarvis", trust=trust)

    def get_phone_numbers(self) -> List[str]:
        """Retrieve all stored phone numbers."""
        return [
            fact.text
            for fact in self.list()
            if fact.text.startswith("Phone:")
        ]

    def get_sim_details(self) -> List[str]:
        """Retrieve all stored SIM details."""
        return [
            fact.text
            for fact in self.list()
            if fact.text.startswith("SIM ")
        ]

    def get_preferences(self) -> List[str]:
        """Retrieve all stored user preferences."""
        return [
            fact.text
            for fact in self.list()
            if fact.text.startswith("Preference:")
        ]

    def search_facts(self, query: str) -> List[Fact]:
        """Search facts by keyword."""
        query_lower = query.lower()
        return [
            fact
            for fact in self.list()
            if query_lower in fact.text.lower()
        ]


def create_jarvis_fact_store(
    path: str | Path | None = None,
    max_facts: int = 5000,
) -> JARVISFactStore:
    """Create a JARVIS fact store with sensible defaults."""
    return JARVISFactStore(path, max_facts=max_facts)


__all__ = [
    "JARVISFactStore",
    "create_jarvis_fact_store",
    "FACT_CATEGORY_PHONE",
    "FACT_CATEGORY_USSD",
    "FACT_CATEGORY_SIM",
    "FACT_CATEGORY_NETWORK",
    "FACT_CATEGORY_PREF",
    "FACT_CATEGORY_COMMAND",
]