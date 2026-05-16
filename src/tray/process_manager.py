"""Subprocess manager for service orchestration."""

from __future__ import annotations

import subprocess
import threading
import time
from dataclasses import dataclass, field


@dataclass
class ProcessManager:
    """Launch and manage child services."""

    procs: dict[str, subprocess.Popen] = field(default_factory=dict)
    commands: dict[str, list[str]] = field(default_factory=dict)
    _monitor_thread: threading.Thread | None = None
    _monitor_running: bool = False

    def start(self, name: str, args: list[str]) -> None:
        """Start process by name."""
        self.stop(name)
        self.commands[name] = list(args)
        self.procs[name] = subprocess.Popen(args)

    def stop(self, name: str) -> None:
        """Stop process by name."""
        proc = self.procs.get(name)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        self.procs.pop(name, None)

    def stop_all(self) -> None:
        """Stop all managed processes."""
        for name in list(self.procs):
            self.stop(name)
        self._monitor_running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=1.0)

    def is_running(self, name: str) -> bool:
        """Return whether a named process is alive."""
        proc = self.procs.get(name)
        return proc is not None and proc.poll() is None

    def start_monitoring(self, interval_s: float = 2.0) -> None:
        """Auto-restart known services when they exit unexpectedly."""
        if self._monitor_running:
            return
        self._monitor_running = True

        def loop() -> None:
            while self._monitor_running:
                for name, proc in list(self.procs.items()):
                    if proc.poll() is not None and name in self.commands:
                        self.procs[name] = subprocess.Popen(self.commands[name])
                time.sleep(interval_s)

        self._monitor_thread = threading.Thread(target=loop, daemon=True)
        self._monitor_thread.start()
