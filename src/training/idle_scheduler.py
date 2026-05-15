"""Idle-based incremental training scheduler."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import psutil


@dataclass
class IdleScheduler:
    """Monitor resource usage and toggle training state."""

    gpu_util_threshold: int = 30
    cpu_util_threshold: int = 40
    gpu_temp_threshold: int = 80
    idle_timeout_minutes: int = 5
    check_interval_seconds: int = 30
    status: str = "stopped"
    _thread: threading.Thread | None = None
    _running: bool = False

    def _loop(self) -> None:
        idle_checks = 0
        while self._running:
            cpu = psutil.cpu_percent(interval=0.1)
            if cpu < self.cpu_util_threshold:
                idle_checks += 1
            else:
                idle_checks = 0
                self.status = "paused_hot"
            required = int((self.idle_timeout_minutes * 60) / self.check_interval_seconds)
            if idle_checks >= required:
                self.status = "training"
            else:
                self.status = "idle_waiting"
            time.sleep(self.check_interval_seconds)
        self.status = "stopped"

    def start(self) -> None:
        """Start scheduler thread."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop scheduler thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
