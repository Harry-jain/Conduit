"""Pipeline metrics state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PipelineMetrics:
    e2e_latency_ms: float = 0.0
    asr_wer_est: float = 0.0
    asr_latency_ms: float = 0.0
    mt_latency_ms: float = 0.0
    tts_latency_ms: float = 0.0
