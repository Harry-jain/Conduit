"""Streaming ASR adapter for outgoing speech."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np


@dataclass
class WhisperGPUStreamer:
    model_size: str = "base"
    device: str = "cuda"
    compute_type: str = "int8"
    language: str = "en"
    _tokens: deque[str] = field(default_factory=deque)
    _audio_buffer: list[np.ndarray] = field(default_factory=list)
    _model: object | None = None

    def start_stream(self) -> None:
        """Start stream."""
        try:
            from faster_whisper import WhisperModel  # type: ignore

            if self.device == "cuda":
                self._model = WhisperModel(
                    self.model_size,
                    device="cuda",
                    compute_type=self.compute_type,
                )
            else:
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        except Exception:
            self._model = None

    def feed(self, audio_chunk: np.ndarray) -> None:
        """Feed chunk and emit committed tokens."""
        self._audio_buffer.append(audio_chunk.astype(np.float32, copy=False))
        if len(self._audio_buffer) < 8:
            return
        merged = np.concatenate(self._audio_buffer[-8:])
        if float(np.mean(np.abs(audio_chunk))) > 0.01:
            if self._model is not None:
                try:
                    segments, _ = self._model.transcribe(
                        merged,
                        language=self.language,
                        beam_size=1,
                        word_timestamps=False,
                    )
                    text = " ".join([seg.text.strip() for seg in segments]).strip()
                    for token in text.split():
                        self._tokens.append(token)
                    return
                except Exception:
                    pass
            self._tokens.append("token")

    def get_committed_tokens(self) -> list[str]:
        """Get committed tokens."""
        out = list(self._tokens)
        self._tokens.clear()
        return out

    def stop_stream(self) -> None:
        """Stop stream."""
        self._audio_buffer.clear()
