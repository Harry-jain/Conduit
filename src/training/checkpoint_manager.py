"""Checkpoint save/load/rollback manager."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import torch


@dataclass
class CheckpointManager:
    """Manage checkpoint files and latest alias."""

    checkpoint_dir: str = "models/lora"
    mcd_threshold: float = 6.0
    secs_threshold: float = 0.80

    def save(self, state: dict, epoch: int, step: int) -> str:
        """Save checkpoint and update latest copy."""
        out_dir = Path(self.checkpoint_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"checkpoint_{epoch}_{step}.safetensors"
        torch.save(state, path)
        latest = out_dir / "latest.safetensors"
        shutil.copy2(path, latest)
        return str(path)

    def load(self, path: str) -> dict:
        """Load checkpoint."""
        return torch.load(path, map_location="cpu")

    def save_with_quality_gate(
        self,
        state: dict,
        epoch: int,
        step: int,
        mcd: float,
        secs: float,
    ) -> tuple[str | None, bool]:
        """Save checkpoint only when quality metrics pass configured thresholds."""
        if mcd > self.mcd_threshold or secs < self.secs_threshold:
            return (None, False)
        path = self.save(state=state, epoch=epoch, step=step)
        return (path, True)
