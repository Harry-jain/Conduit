"""Virtual microphone ring-buffer writer."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np


@dataclass
class VirtualMicWriter:
    device_name: str
    sample_rate: int = 22050
    buffer_ms: int = 20
    _opened: bool = False
    _buffer: deque[np.ndarray] = field(default_factory=deque)

    def open(self) -> None:
        """Open writer."""
        self._opened = True

    def write(self, audio_chunk_float32: np.ndarray) -> None:
        """Non-blocking enqueue of float32 audio chunk."""
        if not self._opened:
            raise RuntimeError("Virtual mic writer is not open.")
        self._buffer.append(audio_chunk_float32.astype(np.float32, copy=False))

    def close(self) -> None:
        """Close writer."""
        self._opened = False
        self._buffer.clear()
