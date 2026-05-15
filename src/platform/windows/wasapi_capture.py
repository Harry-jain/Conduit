"""Windows WASAPI microphone capture backend."""

from __future__ import annotations


def backend_name() -> str:
    """Return backend name."""
    return "wasapi_capture"
