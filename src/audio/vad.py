"""Simple VAD detector with frame-level bookkeeping."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class VADResult:
    is_speech: bool
    probability: float
    segment_complete: bool


class VADDetector:
    """Energy-based VAD fallback compatible with Silero-style interface."""

    def __init__(
        self,
        sample_rate: int = 16000,
        threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 300,
    ) -> None:
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.min_speech_frames = max(int(min_speech_duration_ms / 32), 1)
        self.min_silence_frames = max(int(min_silence_duration_ms / 32), 1)
        self._speech_frames = 0
        self._silence_frames = 0

    def process(self, chunk_float32: np.ndarray) -> VADResult:
        """Process one chunk and return speech state."""
        energy = float(np.sqrt(np.mean(np.square(chunk_float32)) + 1e-9))
        probability = max(0.0, min(1.0, energy * 6.0))
        is_speech = probability >= self.threshold
        if is_speech:
            self._speech_frames += 1
            self._silence_frames = 0
        else:
            self._silence_frames += 1
        segment_complete = (
            self._speech_frames >= self.min_speech_frames
            and self._silence_frames >= self.min_silence_frames
        )
        if segment_complete:
            self._speech_frames = 0
            self._silence_frames = 0
        return VADResult(is_speech=is_speech, probability=probability, segment_complete=segment_complete)
