"""Loguru logger setup."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_dir: str = "./logs") -> None:
    """Configure global loguru sinks."""
    level = os.getenv("VOICETRANSLATE_LOG_LEVEL", "INFO").upper()
    rotation = os.getenv("VOICETRANSLATE_LOG_ROTATION", "10 MB")
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        Path(log_dir) / "voicetranslate.log",
        level=level,
        rotation=rotation,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(sys.stderr, level=level)
