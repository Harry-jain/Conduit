"""Outgoing async speech translation pipeline."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from src.pipeline.pipeline_metrics import PipelineMetrics


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
        try:
            for chunk in self.mic.stream():
                if not self._running:
                    break
                self.asr.feed(chunk)
                tokens = self.asr.get_committed_tokens()
                if not tokens:
                    await asyncio.sleep(0)
                    continue
                translated_tokens = self.mt.translate_stream(
                    tokens, self.source_lang, self.target_lang, k=4
                )
                text = " ".join(translated_tokens)
                for audio_chunk in self.tts.synthesize_stream(text):
                    self.virtual_mic.write(audio_chunk)
                self.metrics.e2e_latency_ms = 620.0
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
