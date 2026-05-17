"""LoRA checkpoint loader and watcher."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoRAWatcher:
    checkpoint_path: str
    _last_mtime: float = 0.0
    _cached_state: dict | None = None

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

    def load_if_updated(self) -> dict | None:
        """Load and cache checkpoint state when file changes."""
        if not self.has_update():
            return self._cached_state
        p = Path(self.checkpoint_path)
        if not p.exists():
            return self._cached_state
        if p.suffix == ".safetensors":
            try:
                from safetensors.torch import load_file  # type: ignore

                self._cached_state = dict(load_file(str(p)))
                return self._cached_state
            except (ImportError, OSError, ValueError, RuntimeError):
                return self._cached_state
        try:
            import torch

            state = torch.load(str(p), map_location="cpu")
            self._cached_state = dict(state) if isinstance(state, dict) else {"state": state}
            return self._cached_state
        except (ImportError, OSError, ValueError, RuntimeError):
            return self._cached_state
