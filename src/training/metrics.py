"""Training quality metrics."""

from __future__ import annotations

import numpy as np


def compute_mcd(mel_a: np.ndarray, mel_b: np.ndarray) -> float:
    """Compute simple mel cepstral distortion proxy."""
    diff = mel_a - mel_b
    return float(np.mean(np.abs(diff)))


def compute_secs(emb_a: np.ndarray, emb_b: np.ndarray) -> float:
    """Compute speaker embedding cosine similarity."""
    return float(np.dot(emb_a, emb_b) / ((np.linalg.norm(emb_a) * np.linalg.norm(emb_b)) + 1e-9))
