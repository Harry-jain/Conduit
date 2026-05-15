"""Overlay position calculations."""

from __future__ import annotations


def position_above_taskbar(screen_width: int, screen_height: int, taskbar_height: int, overlay_height: int = 80) -> tuple[int, int, int, int]:
    """Return x, y, width, height for bottom overlay."""
    return (0, screen_height - taskbar_height - overlay_height, screen_width, overlay_height)
