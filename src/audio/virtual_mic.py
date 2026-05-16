"""Virtual microphone ring-buffer writer."""

from __future__ import annotations

import platform
from dataclasses import dataclass

import numpy as np

from src.platform.macos.virtual_cable import MacOSVirtualCableWriter
from src.platform.windows.virtual_cable import WindowsVirtualCableWriter


@dataclass
class VirtualMicWriter:
    device_name: str
    sample_rate: int = 22050
    buffer_ms: int = 20
    _opened: bool = False
    _backend: WindowsVirtualCableWriter | MacOSVirtualCableWriter | None = None

    def open(self) -> None:
        """Open writer."""
        system = platform.system().lower()
        if system == "windows":
            self._backend = WindowsVirtualCableWriter(
                device_name=self.device_name,
                sample_rate=self.sample_rate,
                buffer_ms=self.buffer_ms,
            )
        else:
            self._backend = MacOSVirtualCableWriter(
                device_name=self.device_name,
                sample_rate=self.sample_rate,
                buffer_ms=self.buffer_ms,
            )
        self._backend.open()
        self._opened = True

    def write(self, audio_chunk_float32: np.ndarray) -> None:
        """Non-blocking enqueue of float32 audio chunk."""
        if not self._opened:
            raise RuntimeError("Virtual mic writer is not open.")
        if self._backend is not None:
            self._backend.write(audio_chunk_float32.astype(np.float32, copy=False))

    def close(self) -> None:
        """Close writer."""
        if self._backend is not None:
            self._backend.close()
        self._opened = False
