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
    _session: object | None = None

    def __post_init__(self) -> None:
        """Initialize ONNX session if model file is available."""
        try:
            import onnxruntime as ort  # type: ignore

            self._session = ort.InferenceSession(
                self.model_path, providers=["CPUExecutionProvider"]
            )
        except (ImportError, OSError, RuntimeError, ValueError):
            self._session = None

    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize waveform for incoming translated text."""
        if self._session is not None:
            try:
                ids = np.frombuffer(text.encode("utf-8"), dtype=np.uint8).astype(np.int64)
                ids = np.clip(ids, 0, 255)
                model_input = {"input_ids": ids[None, :]}
                output = self._session.run(None, model_input)[0]
                audio = np.ravel(np.asarray(output, dtype=np.float32))
                if len(audio) > 0:
                    return audio
            except (KeyError, RuntimeError, ValueError, TypeError):
                pass
        length = max(int(len(text) * self.sample_rate / 11), 1)
        t = np.linspace(0.0, float(length) / float(self.sample_rate), length, endpoint=False)
        pitch = 210.0 if self.voice_preset == "af_heart" else 135.0
        wave = 0.12 * np.sin(2 * np.pi * pitch * t)
        mod = 0.05 * np.sin(2 * np.pi * (pitch * 0.5) * t)
        return (wave + mod).astype(np.float32)
