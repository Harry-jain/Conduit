"""Keyword spotting for DONE command."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class KeywordResult:
    keyword_detected: bool
    confidence: float


class KeywordSpotter:
    """Streaming keyword spotter with text-hook fallback."""

    def __init__(self, keyword: str = "done", confidence_threshold: float = 0.7) -> None:
        self.keyword = keyword.lower()
        self.confidence_threshold = confidence_threshold
        self._active = False

    def start_listening(self) -> None:
        """Enable keyword detection."""
        self._active = True

    def process(self, audio_chunk: np.ndarray | str) -> KeywordResult:
        """Process chunk and detect keyword in text mode."""
        if not self._active:
            return KeywordResult(False, 0.0)
        if isinstance(audio_chunk, str):
            detected = self.keyword in audio_chunk.lower().split()[-3:]
            return KeywordResult(detected, 0.9 if detected else 0.1)
        energy = float(np.mean(np.abs(audio_chunk)))
        return KeywordResult(False, min(energy, 1.0))
