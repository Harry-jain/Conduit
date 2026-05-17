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
    _cosyvoice: object | None = None

    def __post_init__(self) -> None:
        """Try loading CosyVoice runtime when available."""
        try:
            from cosyvoice.cli.cosyvoice import CosyVoice  # type: ignore

            self._cosyvoice = CosyVoice(self.model_path)
        except (ImportError, OSError, RuntimeError, ValueError):
            self._cosyvoice = None

    def synthesize_stream(self, text: str) -> Iterator[np.ndarray]:
        """Yield streaming chunks for given text."""
        if not text:
            return
        if self._cosyvoice is not None:
            try:
                stream = self._cosyvoice.inference_sft(  # type: ignore[attr-defined]
                    text=text,
                    spk_emb=self.speaker_embedding,
                )
                for packet in stream:
                    chunk = np.ravel(np.asarray(packet["tts_speech"], dtype=np.float32))
                    if len(chunk) > 0:
                        yield chunk
                return
            except (KeyError, RuntimeError, ValueError, TypeError):
                pass

        samples_per_chunk = max(int(22050 * 0.116), 1)
        base_hz = 160.0
        for idx, _ in enumerate(text.split()):
            t = np.linspace(0.0, 0.116, samples_per_chunk, endpoint=False, dtype=np.float32)
            hz = base_hz + (idx % 5) * 20.0
            wave = 0.15 * np.sin(2 * np.pi * hz * t)
            env = np.linspace(0.2, 1.0, samples_per_chunk, dtype=np.float32)
            yield (wave * env).astype(np.float32, copy=False)
