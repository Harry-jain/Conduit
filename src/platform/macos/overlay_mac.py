"""macOS NSPanel overlay helpers."""

from __future__ import annotations


def window_level() -> int:
    """Return NSFloatingWindowLevel + 1 when available."""
    try:
        from AppKit import NSFloatingWindowLevel  # type: ignore

        return int(NSFloatingWindowLevel + 1)
    except (ImportError, AttributeError):
        return 1
