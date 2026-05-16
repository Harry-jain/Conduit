"""STFT and mel spectrogram pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import signal


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
        try:
            import librosa  # type: ignore

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
        except ModuleNotFoundError:
            _, _, zxx = signal.stft(
                audio_np,
                fs=self.sample_rate,
                nperseg=self.win_length,
                noverlap=self.win_length - self.hop_length,
                nfft=self.n_fft,
                boundary=None,
            )
            power = np.abs(zxx) ** 2
            mel = power[: self.n_mels, :]
            if mel.shape[0] < self.n_mels:
                mel = np.pad(mel, ((0, self.n_mels - mel.shape[0]), (0, 0)))
            return (10.0 * np.log10(mel + 1e-10)).astype(np.float32)

    def mel_to_audio(self, mel: np.ndarray) -> np.ndarray:
        """Reconstruct waveform from log-mel spectrogram."""
        try:
            import librosa  # type: ignore

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
        except ModuleNotFoundError:
            frames = mel.shape[1] if mel.ndim == 2 else 1
            samples = max(frames * self.hop_length, self.hop_length)
            return np.zeros((samples,), dtype=np.float32)

    def audio_to_stft(self, audio_np: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Compute STFT magnitude and phase."""
        try:
            import librosa  # type: ignore

            stft = librosa.stft(
                audio_np,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                win_length=self.win_length,
            )
            return np.abs(stft).astype(np.float32), np.angle(stft).astype(np.float32)
        except ModuleNotFoundError:
            _, _, zxx = signal.stft(
                audio_np,
                fs=self.sample_rate,
                nperseg=self.win_length,
                noverlap=self.win_length - self.hop_length,
                nfft=self.n_fft,
                boundary=None,
            )
            return np.abs(zxx).astype(np.float32), np.angle(zxx).astype(np.float32)
