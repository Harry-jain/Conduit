"""System loopback capture."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass
class SystemLoopbackCapture:
    target_device: str | None
    sample_rate: int = 48000
    chunk_ms: int = 32
    _running: bool = False

    def start(self) -> None:
        """Start loopback."""
        self._running = True

    def stream(self) -> Iterator[np.ndarray]:
        """Yield downmixed mono float32 chunks."""
        chunk = int(self.sample_rate * (self.chunk_ms / 1000.0))
        while self._running:
            yield np.zeros((chunk,), dtype=np.float32)

    def stop(self) -> None:
        """Stop loopback."""
        self._running = False
