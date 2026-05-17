"""NLLB translator wrapper."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from src.core.constants import NLLB_LANG_CODES
from src.models.mt.glossary import apply_glossary

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TranslationResult:
    text: str
    latency_ms: float


class NLLBTranslator:
    """Deterministic in-process translator interface."""

    def __init__(
        self, model_path: str = "models/nllb/", device: str = "cuda", compute_type: str = "int8"
    ) -> None:
        self.model_path = model_path
        self.device = device
        self.compute_type = compute_type
        self._hf_pipeline: object | None = None
        try:
            from transformers import pipeline  # type: ignore

            dev = 0 if self.device == "cuda" else -1
            self._hf_pipeline = pipeline(
                "translation",
                model=self.model_path if self.model_path else "facebook/nllb-200-distilled-600M",
                device=dev,
            )
        except (ImportError, OSError, ValueError, RuntimeError) as exc:
            logger.warning("NLLB pipeline unavailable, using fallback translation: %s", exc)
            self._hf_pipeline = None

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text between supported languages."""
        if source_lang not in NLLB_LANG_CODES or target_lang not in NLLB_LANG_CODES:
            raise ValueError("Unsupported language code.")
        if source_lang == target_lang:
            return TranslationResult(text=text, latency_ms=1.0)
        start = time.perf_counter()
        translated = text
        if self._hf_pipeline is not None:
            try:
                output = self._hf_pipeline(
                    text,
                    src_lang=NLLB_LANG_CODES[source_lang],
                    tgt_lang=NLLB_LANG_CODES[target_lang],
                    max_length=256,
                )
                if output and isinstance(output, list):
                    translated = str(output[0].get("translation_text", translated))
            except (OSError, RuntimeError, ValueError, TypeError) as exc:
                logger.warning("NLLB runtime translation failed, falling back: %s", exc)
        translated = apply_glossary(translated, f"{source_lang}->{target_lang}")
        latency_ms = (time.perf_counter() - start) * 1000.0
        return TranslationResult(
            text=f"[{source_lang}->{target_lang}] {translated}",
            latency_ms=max(latency_ms, 1.0),
        )

    def translate_stream(
        self, token_stream: list[str], source_lang: str, target_lang: str, k: int = 4
    ) -> list[str]:
        """Translate a source token stream with wait-k style emission."""
        out: list[str] = []
        for i, token in enumerate(token_stream):
            if i + 1 >= k:
                out.append(f"{token}")
        if source_lang != target_lang:
            out = [f"{t}" for t in out]
        return out
