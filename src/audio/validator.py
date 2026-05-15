"""Recording quality validator."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ValidationResult:
    accepted: bool
    snr_db: float
    clipping_pct: float
    rejection_reason: str | None


class AudioValidator:
    """Validate recording duration, SNR, and clipping."""

    def __init__(
        self,
        sample_rate: int = 16000,
        min_duration_s: float = 3.0,
        max_duration_s: float = 30.0,
        min_snr_db: float = 15.0,
        max_clipping_pct: float = 0.01,
    ) -> None:
        self.sample_rate = sample_rate
        self.min_duration_s = min_duration_s
        self.max_duration_s = max_duration_s
        self.min_snr_db = min_snr_db
        self.max_clipping_pct = max_clipping_pct

    def validate(self, audio: np.ndarray) -> ValidationResult:
        """Validate audio and return result."""
        duration_s = len(audio) / float(self.sample_rate)
        clipping_pct = float(np.mean(np.abs(audio) >= 0.999))
        signal_rms = float(np.sqrt(np.mean(np.square(audio)) + 1e-9))
        noise_floor = float(np.percentile(np.abs(audio), 10) + 1e-9)
        snr_db = 20.0 * float(np.log10(signal_rms / noise_floor))
        reason: str | None = None
        if duration_s < self.min_duration_s:
            reason = "duration_too_short"
        elif duration_s > self.max_duration_s:
            reason = "duration_too_long"
        elif snr_db < self.min_snr_db:
            reason = "snr_too_low"
        elif clipping_pct > self.max_clipping_pct:
            reason = "clipping_detected"
        return ValidationResult(
            accepted=reason is None,
            snr_db=snr_db,
            clipping_pct=clipping_pct,
            rejection_reason=reason,
        )
