"""Model download helpers."""

from __future__ import annotations

from pathlib import Path


def ensure_model_dirs(base_dir: str = "models") -> None:
    """Create all required model directories."""
    for name in ["whisper", "nllb", "cosyvoice", "kokoro", "speaker", "lora"]:
        Path(base_dir, name).mkdir(parents=True, exist_ok=True)
