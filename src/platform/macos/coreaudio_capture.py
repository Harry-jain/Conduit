"""CoreAudio capture backend."""

from __future__ import annotations


def backend_name() -> str:
    """Return backend name."""
    return "coreaudio_capture"
