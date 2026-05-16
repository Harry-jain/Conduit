"""MFCC extraction utilities."""

from __future__ import annotations

import numpy as np
from scipy.fftpack import dct


def compute_mfcc(audio: np.ndarray, sample_rate: int = 16000, n_mfcc: int = 13) -> np.ndarray:
    """Compute MFCC with delta and delta-delta features."""
    try:
        import librosa  # type: ignore

        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)
        delta = librosa.feature.delta(mfcc)
        delta2 = librosa.feature.delta(mfcc, order=2)
        return np.concatenate([mfcc, delta, delta2], axis=0).astype(np.float32)
    except ModuleNotFoundError:
        frame = 400
        hop = 160
        if len(audio) < frame:
            audio = np.pad(audio, (0, frame - len(audio)))
        frames = np.stack(
            [audio[i : i + frame] for i in range(0, len(audio) - frame + 1, hop)], axis=0
        )
        win = np.hamming(frame)
        spec = np.abs(np.fft.rfft(frames * win[None, :], axis=1)) ** 2
        log_spec = np.log(spec + 1e-10)
        mfcc = dct(log_spec, axis=1, type=2, norm="ortho")[:, :n_mfcc].T
        delta = np.gradient(mfcc, axis=1)
        delta2 = np.gradient(delta, axis=1)
        return np.concatenate([mfcc, delta, delta2], axis=0).astype(np.float32)
