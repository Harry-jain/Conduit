"""Cross-platform microphone capture wrapper."""

from __future__ import annotations

import platform
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from src.platform.macos.coreaudio_capture import CoreAudioMicrophoneCapture
from src.platform.windows.wasapi_capture import WasapiMicrophoneCapture


@dataclass
class MicrophoneCapture:
    device_name: str | None
    sample_rate: int = 16000
    chunk_ms: int = 32
    exclusive_mode: bool = True
    _running: bool = False
    _backend: WasapiMicrophoneCapture | CoreAudioMicrophoneCapture | None = None

    def start(self) -> None:
        """Start capture."""
        system = platform.system().lower()
        if system == "windows":
            self._backend = WasapiMicrophoneCapture(
                device_name=self.device_name,
                sample_rate=self.sample_rate,
                chunk_ms=self.chunk_ms,
                exclusive_mode=self.exclusive_mode,
            )
        else:
            self._backend = CoreAudioMicrophoneCapture(
                device_name=self.device_name,
                sample_rate=self.sample_rate,
                chunk_ms=self.chunk_ms,
            )
        self._backend.start()
        self._running = True

    def stream(self) -> Iterator[np.ndarray]:
        """Yield platform backend chunks."""
        if self._backend is None:
            chunk = int(self.sample_rate * (self.chunk_ms / 1000.0))
            while self._running:
                yield np.zeros((chunk,), dtype=np.float32)
            return
        yield from self._backend.stream()

    def stop(self) -> None:
        """Stop capture."""
        self._running = False
        if self._backend is not None:
            self._backend.stop()
