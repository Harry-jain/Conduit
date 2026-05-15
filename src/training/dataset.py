"""Dataset definitions for LoRA training."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class MelPairDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    """Dataset of mel input/target pairs from .npy files."""

    def __init__(self, data_dir: str = "data/training") -> None:
        self.paths = sorted(Path(data_dir).glob("*_mel.npy"))

    def __len__(self) -> int:
        """Return sample count."""
        return len(self.paths)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Return mel input and target tensors."""
        mel = np.load(self.paths[index]).astype(np.float32)
        x = torch.from_numpy(mel)
        return x, x
