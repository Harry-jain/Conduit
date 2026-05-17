"""Outgoing async speech translation pipeline."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from src.pipeline.pipeline_metrics import PipelineMetrics

logger = logging.getLogger(__name__)


@dataclass
class OutgoingTranslationPipeline:
    source_lang: str
    target_lang: str
    asr: object
    mt: object
    tts: object
    mic: object
    virtual_mic: object
    metrics: PipelineMetrics = field(default_factory=PipelineMetrics)
    _task: asyncio.Task[None] | None = None
    _running: bool = False

    async def _run(self) -> None:
        self.mic.start()
        self.virtual_mic.open()
        self.asr.start_stream()
        processed = 0
        e2e_total = 0.0
        try:
            for chunk in self.mic.stream():
                if not self._running:
                    break
                start_e2e = time.perf_counter()
                try:
                    start_asr = time.perf_counter()
                    self.asr.feed(chunk)
                    tokens = self.asr.get_committed_tokens()
                    self.metrics.asr_latency_ms = (time.perf_counter() - start_asr) * 1000.0
                    if not tokens:
                        await asyncio.sleep(0)
                        continue

                    start_mt = time.perf_counter()
                    translated_tokens = self.mt.translate_stream(
                        tokens, self.source_lang, self.target_lang, k=4
                    )
                    self.metrics.mt_latency_ms = (time.perf_counter() - start_mt) * 1000.0

                    start_tts = time.perf_counter()
                    text = " ".join(translated_tokens)
                    for audio_chunk in self.tts.synthesize_stream(text):
                        self.virtual_mic.write(audio_chunk)
                    self.metrics.tts_latency_ms = (time.perf_counter() - start_tts) * 1000.0
                except Exception as exc:
                    logger.exception("Outgoing chunk failed and was skipped: %s", exc)
                    await asyncio.sleep(0)
                    continue

                e2e_ms = (time.perf_counter() - start_e2e) * 1000.0
                processed += 1
                e2e_total += e2e_ms
                self.metrics.e2e_latency_ms = e2e_total / float(processed)
                await asyncio.sleep(0)
        finally:
            self.asr.stop_stream()
            self.mic.stop()
            self.virtual_mic.close()

    async def start(self) -> None:
        """Start non-blocking outgoing pipeline."""
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop outgoing pipeline."""
        self._running = False
        if self._task is not None:
            await asyncio.wait([self._task], timeout=1.0)
