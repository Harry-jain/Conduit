"""F0 extraction via pyworld."""

from __future__ import annotations

import numpy as np


def extract_f0(audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
    """Extract F0 contour."""
    try:
        import pyworld as pw  # type: ignore
    except ModuleNotFoundError:
        window = 320
        hop = 160
        out = []
        for i in range(0, max(len(audio) - window, 1), hop):
            frame = audio[i : i + window]
            signs = np.signbit(frame)
            zc = np.count_nonzero(signs[:-1] != signs[1:])
            freq = (zc * sample_rate) / (2.0 * max(len(frame), 1))
            out.append(float(freq if 50.0 <= freq <= 500.0 else 0.0))
        return np.array(out, dtype=np.float32)
    f0, _ = pw.dio(audio.astype(np.float64), fs=sample_rate)
    return f0.astype(np.float32)
