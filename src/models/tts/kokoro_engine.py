"""Incoming generic-voice TTS engine."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class KokoroEngine:
    model_path: str
    voice_preset: str = "af_heart"
    device: str = "cpu"
    sample_rate: int = 22050

    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize waveform for incoming translated text."""
        length = max(int(len(text) * self.sample_rate / 10), 1)
        return np.zeros((length,), dtype=np.float32)
