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
        self._buffer: list[np.ndarray] = []
        self._sample_rate = 16000
        self._model: object | None = None
        try:
            from faster_whisper import WhisperModel  # type: ignore

            self._model = WhisperModel("tiny", device="cpu", compute_type="int8")
        except (ImportError, OSError, RuntimeError, ValueError):
            self._model = None

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
        chunk = audio_chunk.astype(np.float32, copy=False)
        self._buffer.append(chunk)
        merged = np.concatenate(self._buffer) if self._buffer else chunk
        if len(merged) >= self._sample_rate and self._model is not None:
            recent = merged[-self._sample_rate :]
            try:
                segments, _ = self._model.transcribe(
                    recent,
                    language="en",
                    beam_size=1,
                    word_timestamps=False,
                )
                text = " ".join([seg.text.strip() for seg in segments]).strip().lower()
                tail = text.split()[-3:]
                detected = self.keyword in tail
                confidence = 0.9 if detected else 0.2
                if detected and confidence >= self.confidence_threshold:
                    self._buffer.clear()
                    return KeywordResult(True, confidence)
            except (OSError, RuntimeError, ValueError):
                pass
            self._buffer = [merged[-self._sample_rate // 2 :]]
        energy = float(np.mean(np.abs(chunk)))
        return KeywordResult(False, min(energy * 2.0, 1.0))
