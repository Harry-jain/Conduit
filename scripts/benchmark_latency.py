"""Simple benchmark placeholder for pipeline latency estimation."""

from __future__ import annotations

import time


def benchmark() -> dict[str, float]:
    """Measure synthetic stage timings."""
    start = time.perf_counter()
    time.sleep(0.01)
    asr = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    time.sleep(0.01)
    mt = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    time.sleep(0.01)
    tts = (time.perf_counter() - start) * 1000
    return {"asr_ms": asr, "mt_ms": mt, "tts_ms": tts, "e2e_ms": asr + mt + tts}


if __name__ == "__main__":
    benchmark()
