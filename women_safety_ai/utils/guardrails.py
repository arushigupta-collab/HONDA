# women_safety_ai

from __future__ import annotations

import re
from typing import Pattern

_REFUSAL_MESSAGE = (
    "I'm sorry, I can’t discuss explicit or personally identifiable details. "
    "Let's focus on overall safety patterns and helpful, general guidance."
)


def _compile(patterns: list[str]) -> list[Pattern[str]]:
    return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]


EXPLICIT_PATTERNS = _compile(
    [
        r"\bsexual\s+violence\b",
        r"\bsexual\s+assault\b",
        r"\brape\b",
        r"\bgraphic\s+detail\b",
    ]
)

PII_PATTERNS = _compile(
    [
        r"\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b",  # phone numbers
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # emails
        r"\b\d{1,4}\s+\w+\s+(street|st\.|road|rd\.|avenue|ave\.)\b",
    ]
)

SELF_HARM_PATTERNS = _compile(
    [
        r"\bsuicide\b",
        r"\bself[-\s]?harm\b",
        r"\bkill myself\b",
    ]
)

ALL_PATTERNS = EXPLICIT_PATTERNS + PII_PATTERNS + SELF_HARM_PATTERNS


def postprocess(text: str) -> str:
    if not text:
        return text

    for pattern in ALL_PATTERNS:
        if pattern.search(text):
            return _REFUSAL_MESSAGE
    return text


def sanitize_user_input(text: str) -> str:
    if text is None:
        return ""

    sanitized = text.strip()
    for pattern in PII_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized
