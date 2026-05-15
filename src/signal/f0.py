"""F0 extraction via pyworld."""

from __future__ import annotations

import numpy as np
import pyworld as pw


def extract_f0(audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """Extract F0 contour."""
    f0, _ = pw.dio(audio.astype(np.float64), fs=sample_rate)
    return f0.astype(np.float32)
