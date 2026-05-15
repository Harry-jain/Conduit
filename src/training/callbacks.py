"""Training callbacks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EarlyStopping:
    """Simple early stopping callback."""

    patience: int = 3
    best: float = float("inf")
    bad_epochs: int = 0

    def step(self, value: float) -> bool:
        """Return True when training should stop."""
        if value < self.best:
            self.best = value
            self.bad_epochs = 0
            return False
        self.bad_epochs += 1
        return self.bad_epochs >= self.patience
