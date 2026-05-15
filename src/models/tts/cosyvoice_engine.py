"""Outgoing TTS engine interface."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass
class CosyVoiceEngine:
    model_path: str
    speaker_embedding: np.ndarray
    lora_checkpoint: str
    device: str = "cuda"
    streaming: bool = True
    chunk_frames: int = 20

    def synthesize_stream(self, text: str) -> Iterator[np.ndarray]:
        """Yield streaming chunks for given text."""
        if not text:
            return
        chunks = max(len(text) // 12, 1)
        for _ in range(chunks):
            yield np.zeros((2560,), dtype=np.float32)
