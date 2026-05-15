"""LPC formant estimation."""

from __future__ import annotations

import librosa
import numpy as np


def estimate_formants(audio: np.ndarray, sample_rate: int = 16000, order: int = 12) -> np.ndarray:
    """Estimate rough formants F1-F4 using LPC roots."""
    a = librosa.lpc(audio, order=order)
    roots = np.roots(a)
    roots = roots[np.imag(roots) >= 0]
    angles = np.arctan2(np.imag(roots), np.real(roots))
    freqs = sorted(angles * (sample_rate / (2 * np.pi)))
    formants = [f for f in freqs if 90 < f < 5000][:4]
    while len(formants) < 4:
        formants.append(0.0)
    return np.array(formants, dtype=np.float32)
