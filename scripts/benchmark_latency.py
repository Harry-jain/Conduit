"""Pipeline latency benchmark utility."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from src.models.asr.whisper_gpu import WhisperGPUStreamer
from src.models.mt.nllb_engine import NLLBTranslator
from src.models.tts.cosyvoice_engine import CosyVoiceEngine


def benchmark(iterations: int = 20) -> dict[str, float]:
    """Measure stage timings with local model wrappers."""
    asr = WhisperGPUStreamer(language="en")
    mt = NLLBTranslator(device="cpu")
    tts = CosyVoiceEngine(
        model_path="models/cosyvoice/",
        speaker_embedding=np.ones((256,), dtype=np.float32) / 16.0,
        lora_checkpoint="models/lora/latest.safetensors",
        device="cpu",
    )
    asr.start_stream()
    asr_ms: list[float] = []
    mt_ms: list[float] = []
    tts_ms: list[float] = []
    e2e_ms: list[float] = []
    for _ in range(iterations):
        pcm = (np.random.rand(16000 // 2).astype(np.float32) - 0.5) * 0.2
        start_e2e = time.perf_counter()
        start = time.perf_counter()
        asr.feed(pcm)
        tokens = asr.get_committed_tokens() or ["hello", "world"]
        asr_ms.append((time.perf_counter() - start) * 1000.0)

        start = time.perf_counter()
        translated = mt.translate_stream(tokens, "en", "ja", k=1)
        sentence = " ".join(translated) if translated else "hello"
        mt_ms.append((time.perf_counter() - start) * 1000.0)

        start = time.perf_counter()
        generated = 0
        for chunk in tts.synthesize_stream(sentence):
            generated += len(chunk)
            if generated >= 22050:
                break
        tts_ms.append((time.perf_counter() - start) * 1000.0)

        e2e_ms.append((time.perf_counter() - start_e2e) * 1000.0)
    asr.stop_stream()
    return {
        "iterations": float(iterations),
        "asr_ms_avg": float(np.mean(asr_ms)),
        "mt_ms_avg": float(np.mean(mt_ms)),
        "tts_ms_avg": float(np.mean(tts_ms)),
        "e2e_ms_avg": float(np.mean(e2e_ms)),
        "e2e_ms_p95": float(np.percentile(np.asarray(e2e_ms), 95)),
    }


if __name__ == "__main__":
    result = benchmark()
    out = Path("logs/benchmark_latency.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
