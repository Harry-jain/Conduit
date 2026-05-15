"""Cross-platform microphone capture wrapper."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass
class MicrophoneCapture:
    device_name: str | None
    sample_rate: int = 16000
    chunk_ms: int = 32
    exclusive_mode: bool = True
    _running: bool = False

    def start(self) -> None:
        """Start capture."""
        self._running = True

    def stream(self) -> Iterator[np.ndarray]:
        """Yield silent chunks as default fallback source."""
        chunk = int(self.sample_rate * (self.chunk_ms / 1000.0))
        while self._running:
            yield np.zeros((chunk,), dtype=np.float32)

    def stop(self) -> None:
        """Stop capture."""
        self._running = False
