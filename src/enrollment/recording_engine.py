"""Enrollment recording orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from src.audio.validator import AudioValidator
from src.signal.stft import STFTPipeline


@dataclass(frozen=True)
class RecordingResult:
    audio_np: np.ndarray
    duration_s: float
    snr_db: float
    was_clipped: bool
    mel_spectrogram: np.ndarray
    accepted: bool
    rejection_reason: str | None


class RecordingEngine:
    """Record one sentence and persist waveform plus mel features."""

    def __init__(
        self, sample_rate: int = 16000, out_dir: str = "data/enrollment", save_format: str = "wav"
    ) -> None:
        self.sample_rate = sample_rate
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        if save_format not in {"wav", "flac"}:
            raise ValueError("save_format must be 'wav' or 'flac'.")
        self.save_format = save_format
        self.validator = AudioValidator(sample_rate=sample_rate)
        self.stft = STFTPipeline(sample_rate=22050)

    def record_sentence(
        self, sentence_text: str, sentence_index: int = 1, audio_np: np.ndarray | None = None
    ) -> RecordingResult:
        """Validate and save one sentence recording."""
        if audio_np is None:
            audio_np = np.zeros((self.sample_rate * 3,), dtype=np.float32)
        val = self.validator.validate(audio_np)
        duration_s = len(audio_np) / float(self.sample_rate)
        mel = self.stft.audio_to_mel(
            np.interp(
                np.linspace(0, len(audio_np), int(duration_s * 22050), endpoint=False),
                np.arange(len(audio_np)),
                audio_np,
            ).astype(np.float32)
        )
        audio_path = self.out_dir / f"segment_{sentence_index:03d}.{self.save_format}"
        mel_path = self.out_dir / f"segment_{sentence_index:03d}_mel.npy"
        sf.write(audio_path, audio_np, self.sample_rate)
        np.save(mel_path, mel)
        metadata_path = self.out_dir / "metadata.json"
        metadata = {
            "sentence_index": sentence_index,
            "sentence_text": sentence_text,
            "audio_path": str(audio_path),
            "mel_path": str(mel_path),
            "accepted": val.accepted,
        }
        if metadata_path.exists():
            try:
                existing = json.loads(metadata_path.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = [existing]
            except json.JSONDecodeError:
                existing = []
        else:
            existing = []
        existing.append(metadata)
        metadata_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        return RecordingResult(
            audio_np=audio_np,
            duration_s=duration_s,
            snr_db=val.snr_db,
            was_clipped=val.clipping_pct > 0.0,
            mel_spectrogram=mel,
            accepted=val.accepted,
            rejection_reason=val.rejection_reason,
        )
