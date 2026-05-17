"""macOS dock metrics."""

from __future__ import annotations

import subprocess
from shlex import split


def get_dock_height() -> int:
    """Return estimated dock height from macOS Dock preferences."""
    try:
        orientation = subprocess.check_output(
            split("defaults read com.apple.dock orientation"),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if orientation != "bottom":
            return 0
        tile_size_text = subprocess.check_output(
            split("defaults read com.apple.dock tilesize"),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        tile_size = int(float(tile_size_text))
        return max(tile_size + 16, 48)
    except (OSError, ValueError, subprocess.CalledProcessError):
        return 48
