import numpy as np

from src.signal.stft import STFTPipeline


def test_stft_shapes(sine_16k: np.ndarray) -> None:
    stft = STFTPipeline(sample_rate=16000)
    mel = stft.audio_to_mel(sine_16k)
    assert mel.shape[0] == 80
    assert np.isfinite(mel).all()
