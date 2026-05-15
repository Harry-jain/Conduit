import numpy as np

from src.signal.mfcc import compute_mfcc


def test_mfcc_shape(sine_16k: np.ndarray) -> None:
    mfcc = compute_mfcc(sine_16k, sample_rate=16000)
    assert mfcc.shape[0] == 39
    assert np.isfinite(mfcc).all()
