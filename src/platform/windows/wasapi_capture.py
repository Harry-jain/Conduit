"""Windows WASAPI microphone capture backend."""

from __future__ import annotations

import queue
from collections.abc import Iterator
from dataclasses import dataclass, field

import numpy as np
import sounddevice as sd


def _find_device_index_by_name(name: str | None) -> int | None:
    """Resolve sounddevice index by partial case-insensitive name."""
    if not name:
        return None
    needle = name.lower().strip()
    for idx, device in enumerate(sd.query_devices()):
        if needle in str(device["name"]).lower():
            return idx
    return None


@dataclass
class WasapiMicrophoneCapture:
    """WASAPI input stream with optional exclusive mode."""

    device_name: str | None
    sample_rate: int = 16000
    chunk_ms: int = 32
    exclusive_mode: bool = True
    _stream: sd.InputStream | None = None
    _queue: queue.Queue[np.ndarray] = field(default_factory=queue.Queue)
    _running: bool = False

    def start(self) -> None:
        """Start WASAPI microphone capture stream."""
        blocksize = int(self.sample_rate * self.chunk_ms / 1000)
        extra_settings = None
        try:
            extra_settings = sd.WasapiSettings(exclusive=self.exclusive_mode)  # type: ignore[attr-defined]
        except Exception:
            extra_settings = None

        def callback(
            indata: np.ndarray, frames: int, time_info: object, status: sd.CallbackFlags
        ) -> None:
            _ = (frames, time_info)
            if status:
                pass
            mono = (
                indata[:, 0].astype(np.float32, copy=False)
                if indata.ndim == 2
                else indata.astype(np.float32)
            )
            self._queue.put_nowait(mono.copy())

        device_index = _find_device_index_by_name(self.device_name)
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=blocksize,
            dtype="float32",
            channels=1,
            callback=callback,
            device=device_index,
            extra_settings=extra_settings,
        )
        self._stream.start()
        self._running = True

    def stream(self) -> Iterator[np.ndarray]:
        """Yield captured chunks from queue."""
        while self._running:
            try:
                yield self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

    def stop(self) -> None:
        """Stop and close stream."""
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
