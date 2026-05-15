"""Language selection helpers."""

from __future__ import annotations

from src.core.constants import SUPPORTED_LANGUAGES


def available_languages() -> list[tuple[str, str]]:
    """Return supported language code/name pairs."""
    return list(SUPPORTED_LANGUAGES.items())
