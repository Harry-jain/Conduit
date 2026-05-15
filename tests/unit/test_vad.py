import numpy as np

from src.audio.vad import VADDetector


def test_vad_detects_speech_and_segment() -> None:
    vad = VADDetector()
    speech = np.ones((512,), dtype=np.float32) * 0.2
    silence = np.zeros((512,), dtype=np.float32)
    assert vad.process(speech).is_speech
    for _ in range(10):
        result = vad.process(silence)
    assert result.segment_complete
