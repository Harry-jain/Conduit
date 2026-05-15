"""Async queue manager."""

from __future__ import annotations

import asyncio


class QueueManager:
    """Container for stage queues."""

    def __init__(self) -> None:
        self.asr_queue: asyncio.Queue[str] = asyncio.Queue()
        self.tts_queue: asyncio.Queue[str] = asyncio.Queue()
