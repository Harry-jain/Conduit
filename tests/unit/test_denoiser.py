import numpy as np

from src.audio.denoiser import Denoiser


def test_denoiser_shape(sine_16k: np.ndarray) -> None:
    out = Denoiser(sample_rate=16000).reduce(sine_16k)
    assert isinstance(out, np.ndarray)
    assert out.shape == sine_16k.shape
