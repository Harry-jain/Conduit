"""Subprocess manager for service orchestration."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field


@dataclass
class ProcessManager:
    """Launch and manage child services."""

    procs: dict[str, subprocess.Popen] = field(default_factory=dict)

    def start(self, name: str, args: list[str]) -> None:
        """Start process by name."""
        self.stop(name)
        self.procs[name] = subprocess.Popen(args)

    def stop(self, name: str) -> None:
        """Stop process by name."""
        proc = self.procs.get(name)
        if proc is not None and proc.poll() is None:
            proc.terminate()

    def stop_all(self) -> None:
        """Stop all managed processes."""
        for name in list(self.procs):
            self.stop(name)
