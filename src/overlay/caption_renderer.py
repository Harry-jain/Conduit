"""Prefix-stable caption rendering state."""

from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class CaptionRenderer:
    """Maintain committed and partial caption text."""

    committed: str = ""
    partial: str = ""
    last_update_ts: float = 0.0
    opacity: float = 1.0

    def update_partial(self, text: str) -> str:
        """Update volatile suffix while preserving committed prefix."""
        self.partial = text
        self.last_update_ts = time.time()
        self.opacity = 1.0
        return f"{self.committed}{self.partial}"

    def update_committed(self, text: str) -> str:
        """Commit stable caption segment."""
        self.committed = text
        self.partial = ""
        self.last_update_ts = time.time()
        self.opacity = 1.0
        return self.committed

    def tick(self, hold_seconds: float = 3.0, fade_seconds: float = 1.0) -> float:
        """Advance fade state and return current opacity."""
        elapsed = time.time() - self.last_update_ts
        if elapsed <= hold_seconds:
            self.opacity = 1.0
        elif elapsed <= hold_seconds + fade_seconds:
            self.opacity = max(0.0, 1.0 - (elapsed - hold_seconds) / fade_seconds)
        else:
            self.opacity = 0.0
        return self.opacity
