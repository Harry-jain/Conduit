"""Model download helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download
from loguru import logger


@dataclass(frozen=True)
class ModelSpec:
    """Model fetch description."""

    repo_id: str
    local_dir: str
    filename: str | None = None


MODEL_SPECS: tuple[ModelSpec, ...] = (
    ModelSpec(repo_id="Systran/faster-whisper-base", local_dir="whisper"),
    ModelSpec(repo_id="facebook/nllb-200-distilled-600M", local_dir="nllb"),
    ModelSpec(
        repo_id="hexgrad/Kokoro-82M",
        local_dir="kokoro",
        filename="kokoro-v0_19.onnx",
    ),
)


def ensure_model_dirs(base_dir: str = "models") -> dict[str, Path]:
    """Create all required model directories and return their paths."""
    paths: dict[str, Path] = {}
    for name in ["whisper", "nllb", "cosyvoice", "kokoro", "speaker", "lora"]:
        model_path = Path(base_dir, name)
        model_path.mkdir(parents=True, exist_ok=True)
        paths[name] = model_path
    return paths


def download_required_models(base_dir: str = "models") -> None:
    """Download required model artifacts from Hugging Face."""
    paths = ensure_model_dirs(base_dir=base_dir)
    for spec in MODEL_SPECS:
        target_dir = str(paths[spec.local_dir])
        logger.info("Downloading model {} -> {}", spec.repo_id, target_dir)
        if spec.filename:
            hf_hub_download(
                repo_id=spec.repo_id,
                filename=spec.filename,
                local_dir=target_dir,
                local_dir_use_symlinks=False,
            )
            continue
        snapshot_download(
            repo_id=spec.repo_id,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            ignore_patterns=["*.msgpack", "*.h5"],
        )
