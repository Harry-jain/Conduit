"""Shared test fixtures."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture()
def sine_16k() -> np.ndarray:
    """Return synthetic 3-second test audio at 16k."""
    sr = 16000
    t = np.linspace(0, 3.0, int(sr * 3.0), endpoint=False)
    return (0.2 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
