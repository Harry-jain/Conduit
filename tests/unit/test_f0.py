import numpy as np

from src.signal.f0 import extract_f0


def test_f0_extraction(sine_16k: np.ndarray) -> None:
    f0 = extract_f0(sine_16k, sample_rate=16000)
    assert isinstance(f0, np.ndarray)
    assert f0.ndim == 1
