"""macOS NSPanel overlay helpers."""

from __future__ import annotations


def window_level() -> str:
    """Return NSFloatingWindowLevel hint."""
    return "NSFloatingWindowLevel+1"
