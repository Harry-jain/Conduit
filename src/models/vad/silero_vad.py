"""Silero VAD adapter."""

from __future__ import annotations

import numpy as np


def classify_frame(frame: np.ndarray) -> float:
    """Return speech probability proxy in [0,1]."""
    energy = float(np.sqrt(np.mean(np.square(frame)) + 1e-9))
    return max(0.0, min(1.0, energy * 6.0))
