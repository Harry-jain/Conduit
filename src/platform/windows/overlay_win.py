"""Windows overlay helpers."""

from __future__ import annotations


def window_level() -> int:
    """Return HWND_TOPMOST constant."""
    try:
        import win32con  # type: ignore

        return int(win32con.HWND_TOPMOST)
    except (ImportError, AttributeError):
        return -1
