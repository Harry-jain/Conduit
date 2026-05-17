"""Incoming caption and translation pipeline."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from src.pipeline.pipeline_metrics import PipelineMetrics

logger = logging.getLogger(__name__)


@dataclass
class IncomingCaptionPipeline:
    target_lang: str
    asr: object
    language_detector: object
    mt: object
    tts: object
    loopback: object
    caption_overlay: object
    metrics: PipelineMetrics = field(default_factory=PipelineMetrics)
    _task: asyncio.Task[None] | None = None
    _running: bool = False

    async def _run(self) -> None:
        self.loopback.start()
        processed = 0
        e2e_total = 0.0
        try:
            for chunk in self.loopback.stream():
                if not self._running:
                    break
                start_e2e = time.perf_counter()
                try:
                    start_asr = time.perf_counter()
                    text = self.asr.transcribe(chunk)
                    self.metrics.asr_latency_ms = (time.perf_counter() - start_asr) * 1000.0
                    if not text:
                        await asyncio.sleep(0)
                        continue

                    start_mt = time.perf_counter()
                    detected = self.language_detector(text)
                    out = (
                        text
                        if detected == self.target_lang
                        else self.mt.translate(text, detected, self.target_lang).text
                    )
                    self.metrics.mt_latency_ms = (time.perf_counter() - start_mt) * 1000.0

                    self.caption_overlay.update_partial(out)
                    self.caption_overlay.update_committed(out)

                    start_tts = time.perf_counter()
                    self.tts.synthesize(out)
                    self.metrics.tts_latency_ms = (time.perf_counter() - start_tts) * 1000.0
                except Exception as exc:
                    logger.exception("Incoming chunk failed and was skipped: %s", exc)
                    await asyncio.sleep(0)
                    continue

                e2e_ms = (time.perf_counter() - start_e2e) * 1000.0
                processed += 1
                e2e_total += e2e_ms
                self.metrics.e2e_latency_ms = e2e_total / float(processed)
                await asyncio.sleep(0)
        finally:
            self.loopback.stop()

    async def start(self) -> None:
        """Start incoming pipeline."""
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop incoming pipeline."""
        self._running = False
        if self._task is not None:
            await asyncio.wait([self._task], timeout=1.0)
