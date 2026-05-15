"""Spectral denoiser wrapper."""

from __future__ import annotations

import noisereduce as nr
import numpy as np


class Denoiser:
    """Denoise audio chunks with noisereduce."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate

    def reduce(self, audio: np.ndarray) -> np.ndarray:
        """Return denoised audio."""
        return nr.reduce_noise(y=audio, sr=self.sample_rate).astype(np.float32, copy=False)
