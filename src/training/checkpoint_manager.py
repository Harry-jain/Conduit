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
