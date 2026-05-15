"""Wait-k policy implementation."""

from __future__ import annotations


class WaitKPolicy:
    """Emit tokens after first k source tokens."""

    def __init__(self, k: int = 4) -> None:
        self.k = k
        self._src_seen = 0

    def should_emit(self) -> bool:
        """Return whether target token can be emitted."""
        self._src_seen += 1
        return self._src_seen >= self.k
