"""Incoming language detection wrapper."""

from __future__ import annotations

from langdetect import DetectorFactory, LangDetectException, detect_langs

from src.core.constants import SUPPORTED_LANGUAGES

DetectorFactory.seed = 0


def detect_language(text: str) -> str:
    """Detect supported ISO language code from text."""
    normalized = text.strip()
    if not normalized:
        return "en"
    try:
        candidates = detect_langs(normalized)
    except LangDetectException:
        return "en"
    for candidate in candidates:
        code = str(candidate.lang).split("-")[0].lower()
        if code in SUPPORTED_LANGUAGES:
            return code
    return "en"
