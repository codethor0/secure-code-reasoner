"""Utility functions for demo repository."""

from typing import Optional


def validate_input(value: Optional[str]) -> bool:
    """Validate that input is not None and not empty."""
    return value is not None and len(value) > 0


def sanitize_string(text: str) -> str:
    """Remove leading and trailing whitespace."""
    return text.strip()


def process_data(data: list) -> int:
    """Process a list and return its length."""
    return len(data) if data else 0
