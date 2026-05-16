"""CPU ASR for incoming speech."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class WhisperCPUTranscriber:
    """Incoming ASR wrapper with optional faster-whisper backend."""

    model_size: str = "base"
    language: str = "en"
    _model: object | None = None

    def __post_init__(self) -> None:
        try:
            from faster_whisper import WhisperModel  # type: ignore

            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        except Exception:
            self._model = None

    def transcribe(self, audio: bytes | object) -> str:
        """Return decoded text."""
        if self._model is None:
            return ""
        try:
            arr = np.asarray(audio, dtype=np.float32)
            segments, _ = self._model.transcribe(
                arr,
                language=self.language,
                beam_size=1,
                word_timestamps=False,
            )
            return " ".join([seg.text.strip() for seg in segments]).strip()
        except Exception:
            return ""
