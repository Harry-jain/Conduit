"""Runtime status monitor."""

from __future__ import annotations

import sqlite3
import threading
import time
from dataclasses import dataclass, field

from src.core.database import get_connection
from src.core.hardware import HardwareProfile


@dataclass
class StatusMonitor:
    """Expose hardware and latency status."""

    latency_ms: float = 0.0
    db_path: str = "voicetranslate.db"
    poll_interval_s: float = 5.0
    _running: bool = False
    _thread: threading.Thread | None = None
    _snapshot: dict[str, object] = field(
        default_factory=lambda: {
            "gpu_temp_c": 0,
            "vram_free_mb": 0,
            "latency_ms": 0.0,
        }
    )

    def start(self) -> None:
        """Start background polling thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop background polling thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def snapshot(self) -> dict[str, object]:
        """Return current status snapshot."""
        if not self._running:
            self._refresh()
        return dict(self._snapshot)

    def _poll_loop(self) -> None:
        """Continuously refresh status while running."""
        while self._running:
            self._refresh()
            time.sleep(self.poll_interval_s)

    def _refresh(self) -> None:
        """Refresh hardware and latency values."""
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
            conn.close()
        except sqlite3.Error:
            self.latency_ms = float(self._snapshot.get("latency_ms", 0.0))
        self._snapshot = {
            "gpu_temp_c": hw.gpu_temp_celsius,
            "vram_free_mb": hw.vram_free_mb,
            "latency_ms": self.latency_ms,
        }
