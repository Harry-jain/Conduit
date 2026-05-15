import numpy as np

from src.training.metrics import compute_mcd, compute_secs


def test_metrics_values() -> None:
    a = np.ones((80, 10), dtype=np.float32)
    b = np.ones((80, 10), dtype=np.float32)
    assert compute_mcd(a, b) == 0.0
    assert compute_secs(np.ones((4,)), np.ones((4,))) > 0.99
