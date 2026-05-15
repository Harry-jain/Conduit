"""Shared vocoder interfaces."""

from __future__ import annotations

import numpy as np


def mel_to_waveform_stub(mel_frames: int, sample_rate: int = 22050) -> np.ndarray:
    """Generate a silence waveform for a mel chunk count."""
    samples = max(int(mel_frames * 256), 1)
    return np.zeros((samples,), dtype=np.float32)
