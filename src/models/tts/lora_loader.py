"""LoRA checkpoint loader and watcher."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoRAWatcher:
    checkpoint_path: str
    _last_mtime: float = 0.0

    def has_update(self) -> bool:
        """Return whether checkpoint file has changed."""
        p = Path(self.checkpoint_path)
        if not p.exists():
            return False
        mtime = p.stat().st_mtime
        if mtime > self._last_mtime:
            self._last_mtime = mtime
            return True
        return False
