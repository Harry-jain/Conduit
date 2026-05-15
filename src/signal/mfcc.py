"""MFCC extraction utilities."""

from __future__ import annotations

import librosa
import numpy as np


def compute_mfcc(audio: np.ndarray, sample_rate: int = 16000, n_mfcc: int = 13) -> np.ndarray:
    """Compute MFCC with delta and delta-delta features."""
    mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    return np.concatenate([mfcc, delta, delta2], axis=0).astype(np.float32)
