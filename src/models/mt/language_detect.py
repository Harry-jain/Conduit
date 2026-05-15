"""Incoming language detection wrapper."""

from __future__ import annotations

from langdetect import detect


def detect_language(text: str) -> str:
    """Detect ISO language code from text."""
    return detect(text) if text.strip() else "en"
