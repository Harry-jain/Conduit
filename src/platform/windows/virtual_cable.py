"""Windows virtual cable writer backend."""

from __future__ import annotations

import queue
from dataclasses import dataclass, field

import numpy as np
import sounddevice as sd


def _find_device_index_by_name(name: str | None) -> int | None:
    """Resolve output device index by fuzzy name."""
    if not name:
        return None
    needle = name.lower().strip()
    for idx, device in enumerate(sd.query_devices()):
        if needle in str(device["name"]).lower():
            return idx
    return None


@dataclass
class WindowsVirtualCableWriter:
    """Output writer to VB-Cable virtual microphone endpoint."""

    device_name: str
    sample_rate: int = 22050
    buffer_ms: int = 20
    _stream: sd.OutputStream | None = None
    _queue: queue.Queue[np.ndarray] = field(default_factory=queue.Queue)

    def open(self) -> None:
        """Open output stream."""
        blocksize = int(self.sample_rate * self.buffer_ms / 1000)

        def callback(
            outdata: np.ndarray, frames: int, time_info: object, status: sd.CallbackFlags
        ) -> None:
            _ = (time_info, status)
            try:
                chunk = self._queue.get_nowait()
            except queue.Empty:
                outdata.fill(0.0)
                return
            if len(chunk) < frames:
                padded = np.zeros((frames,), dtype=np.float32)
                padded[: len(chunk)] = chunk
                chunk = padded
            outdata[:, 0] = chunk[:frames]

        device_index = _find_device_index_by_name(self.device_name)
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=blocksize,
            dtype="float32",
            channels=1,
            callback=callback,
            device=device_index,
        )
        self._stream.start()

    def write(self, audio_chunk: np.ndarray) -> None:
        """Enqueue chunk for non-blocking playback."""
        self._queue.put_nowait(audio_chunk.astype(np.float32, copy=False))

    def close(self) -> None:
        """Close output stream."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
