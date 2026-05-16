"""System loopback capture."""

from __future__ import annotations

import platform
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from src.platform.macos.blackhole_capture import BlackHoleLoopbackCapture
from src.platform.windows.wasapi_loopback import WasapiLoopbackCapture


@dataclass
class SystemLoopbackCapture:
    target_device: str | None
    sample_rate: int = 48000
    chunk_ms: int = 32
    _running: bool = False
    _backend: WasapiLoopbackCapture | BlackHoleLoopbackCapture | None = None

    def start(self) -> None:
        """Start loopback."""
        system = platform.system().lower()
        if system == "windows":
            self._backend = WasapiLoopbackCapture(
                device_name=self.target_device,
                sample_rate=self.sample_rate,
                chunk_ms=self.chunk_ms,
            )
        else:
            self._backend = BlackHoleLoopbackCapture(
                device_name=self.target_device,
                sample_rate=self.sample_rate,
                chunk_ms=self.chunk_ms,
            )
        self._backend.start()
        self._running = True

    def stream(self) -> Iterator[np.ndarray]:
        """Yield downmixed mono float32 chunks."""
        if self._backend is None:
            chunk = int(self.sample_rate * (self.chunk_ms / 1000.0))
            while self._running:
                yield np.zeros((chunk,), dtype=np.float32)
            return
        yield from self._backend.stream()

    def stop(self) -> None:
        """Stop loopback."""
        self._running = False
        if self._backend is not None:
            self._backend.stop()
