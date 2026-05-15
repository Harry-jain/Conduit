import numpy as np

from src.audio.validator import AudioValidator


def test_validator_rejects_short() -> None:
    validator = AudioValidator(sample_rate=16000)
    audio = np.zeros((16000,), dtype=np.float32)
    result = validator.validate(audio)
    assert not result.accepted
