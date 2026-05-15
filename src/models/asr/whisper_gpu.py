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

    def start_stream(self) -> None:
        """Start stream."""

    def feed(self, audio_chunk: np.ndarray) -> None:
        """Feed chunk and emit synthetic token for non-silent audio."""
        if float(np.mean(np.abs(audio_chunk))) > 0.01:
            self._tokens.append("token")

    def get_committed_tokens(self) -> list[str]:
        """Get committed tokens."""
        out = list(self._tokens)
        self._tokens.clear()
        return out

    def stop_stream(self) -> None:
        """Stop stream."""
