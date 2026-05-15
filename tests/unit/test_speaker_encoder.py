import numpy as np

from src.signal.speaker_encoder import SpeakerEncoder


def test_speaker_embedding_shape(sine_16k: np.ndarray) -> None:
    enc = SpeakerEncoder()
    emb = enc.embed_audio(sine_16k)
    assert emb.shape == (256,)
    assert np.isclose(np.linalg.norm(emb), 1.0, atol=1e-3)
