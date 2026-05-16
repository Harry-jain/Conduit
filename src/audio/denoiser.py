"""Spectral denoiser wrapper."""

from __future__ import annotations

import numpy as np


class Denoiser:
    """Denoise audio chunks with noisereduce."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate

    def reduce(self, audio: np.ndarray) -> np.ndarray:
        """Return denoised audio."""
        try:
            import noisereduce as nr  # type: ignore
        except ModuleNotFoundError:
            return audio.astype(np.float32, copy=False)
        return nr.reduce_noise(y=audio, sr=self.sample_rate).astype(np.float32, copy=False)
