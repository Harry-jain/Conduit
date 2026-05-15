"""Audio resampler helpers."""

from __future__ import annotations

import numpy as np
from scipy import signal


def resample_audio(audio: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """Resample 1D audio between sample rates."""
    if src_rate == dst_rate:
        return audio.astype(np.float32, copy=False)
    samples = int(round(len(audio) * float(dst_rate) / float(src_rate)))
    return signal.resample(audio, samples).astype(np.float32, copy=False)
