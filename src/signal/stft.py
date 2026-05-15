"""STFT and mel spectrogram pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import librosa
import numpy as np


@dataclass
class STFTPipeline:
    sample_rate: int = 22050
    n_fft: int = 1024
    hop_length: int = 256
    win_length: int = 1024
    n_mels: int = 80
    fmin: int = 80
    fmax: int = 8000

    def audio_to_mel(self, audio_np: np.ndarray) -> np.ndarray:
        """Convert waveform to log-mel spectrogram."""
        mel = librosa.feature.melspectrogram(
            y=audio_np,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            n_mels=self.n_mels,
            fmin=self.fmin,
            fmax=self.fmax,
            power=2.0,
        )
        return librosa.power_to_db(mel + 1e-10, ref=1.0).astype(np.float32)

    def mel_to_audio(self, mel: np.ndarray) -> np.ndarray:
        """Reconstruct waveform from log-mel spectrogram."""
        power = librosa.db_to_power(mel)
        audio = librosa.feature.inverse.mel_to_audio(
            power,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
            fmin=self.fmin,
            fmax=self.fmax,
            n_iter=16,
        )
        return audio.astype(np.float32)

    def audio_to_stft(self, audio_np: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Compute STFT magnitude and phase."""
        stft = librosa.stft(
            audio_np,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            win_length=self.win_length,
        )
        return np.abs(stft).astype(np.float32), np.angle(stft).astype(np.float32)
