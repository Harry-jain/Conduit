"""Speaker embedding persistence."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def save_embedding(path: str, embedding: np.ndarray) -> None:
    """Save speaker embedding to .npy."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.save(p, embedding.astype(np.float32))


def load_embedding(path: str) -> np.ndarray:
    """Load speaker embedding from .npy."""
    return np.load(path).astype(np.float32)
