"""Incoming caption and translation pipeline."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class IncomingCaptionPipeline:
    target_lang: str
    asr: object
    language_detector: object
    mt: object
    tts: object
    loopback: object
    caption_overlay: object
    _task: asyncio.Task[None] | None = None
    _running: bool = False

    async def _run(self) -> None:
        self.loopback.start()
        try:
            for chunk in self.loopback.stream():
                if not self._running:
                    break
                text = self.asr.transcribe(chunk)
                if not text:
                    await asyncio.sleep(0)
                    continue
                detected = self.language_detector(text)
                out = (
                    text
                    if detected == self.target_lang
                    else self.mt.translate(text, detected, self.target_lang).text
                )
                self.caption_overlay.update_partial(out)
                self.caption_overlay.update_committed(out)
                self.tts.synthesize(out)
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
