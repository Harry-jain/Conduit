"""Configuration loader based on OmegaConf."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from omegaconf import OmegaConf

from src.core.constants import SUPPORTED_LANGUAGES
from src.core.exceptions import ConfigValidationError


@dataclass(frozen=True)
class AudioConfig:
    sample_rate: int
    chunk_size_ms: int


@dataclass(frozen=True)
class ModelsConfig:
    whisper_path: str


@dataclass(frozen=True)
class TrainingConfig:
    lora_rank: int
    learning_rate: float


@dataclass(frozen=True)
class LanguagesConfig:
    supported: list[str]


@dataclass(frozen=True)
class OverlayConfig:
    height_px: int
    font_size: int


@dataclass(frozen=True)
class Config:
    audio: AudioConfig
    models: ModelsConfig
    training: TrainingConfig
    languages: LanguagesConfig
    overlay: OverlayConfig


def _validate(cfg: Config) -> None:
    missing = [code for code in cfg.languages.supported if code not in SUPPORTED_LANGUAGES]
    if missing:
        raise ConfigValidationError(f"Unsupported language codes: {missing}")


@lru_cache(maxsize=1)
def get_config(config_dir: str = "configs") -> Config:
    """Load and cache application configuration from YAML and env vars."""
    load_dotenv()
    base = OmegaConf.load(Path(config_dir) / "base.yaml")
    languages = OmegaConf.load(Path(config_dir) / "languages.yaml")
    audio = OmegaConf.load(Path(config_dir) / "audio.yaml")
    models = OmegaConf.load(Path(config_dir) / "models.yaml")
    training = OmegaConf.load(Path(config_dir) / "training.yaml")
    overlay = OmegaConf.load(Path(config_dir) / "overlay.yaml")
    merged = OmegaConf.merge(base, languages, audio, models, training, overlay)
    cfg = Config(
        audio=AudioConfig(
            sample_rate=int(merged.microphone.sample_rate),
            chunk_size_ms=int(merged.microphone.chunk_ms),
        ),
        models=ModelsConfig(whisper_path=str(merged.whisper.path)),
        training=TrainingConfig(
            lora_rank=int(merged.lora.rank),
            learning_rate=float(merged.optimizer.learning_rate),
        ),
        languages=LanguagesConfig(supported=[str(x.code) for x in merged.supported]),
        overlay=OverlayConfig(
            height_px=int(merged.window.height_px),
            font_size=int(merged.typography.font_size_px),
        ),
    )
    _validate(cfg)
    return cfg
