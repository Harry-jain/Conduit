"""Windows overlay helpers."""

from __future__ import annotations


def window_level() -> str:
    """Return topmost level hint."""
    return "HWND_TOPMOST"
