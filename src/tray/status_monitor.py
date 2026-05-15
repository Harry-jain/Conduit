"""Runtime status monitor."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.hardware import HardwareProfile


@dataclass
class StatusMonitor:
    """Expose hardware and latency status."""

    latency_ms: float = 0.0

    def snapshot(self) -> dict[str, object]:
        """Return current status snapshot."""
        hw = HardwareProfile.detect()
        return {
            "gpu_temp_c": hw.gpu_temp_celsius,
            "vram_free_mb": hw.vram_free_mb,
            "latency_ms": self.latency_ms,
        }
