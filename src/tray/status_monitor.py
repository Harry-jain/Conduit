"""Runtime status monitor."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.database import get_connection
from src.core.hardware import HardwareProfile


@dataclass
class StatusMonitor:
    """Expose hardware and latency status."""

    latency_ms: float = 0.0
    db_path: str = "voicetranslate.db"

    def snapshot(self) -> dict[str, object]:
        """Return current status snapshot."""
        hw = HardwareProfile.detect()
        try:
            conn = get_connection(self.db_path)
            row = conn.execute(
                """
                SELECT e2e_latency_ms FROM pipeline_metrics
                ORDER BY recorded_at DESC LIMIT 1
                """
            ).fetchone()
            if row is not None:
                self.latency_ms = float(row["e2e_latency_ms"])
        except Exception:
            pass
        return {
            "gpu_temp_c": hw.gpu_temp_celsius,
            "vram_free_mb": hw.vram_free_mb,
            "latency_ms": self.latency_ms,
        }
