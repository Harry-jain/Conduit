"""Glossary constrained-decoding support."""

from __future__ import annotations

DEFAULT_GLOSSARY: dict[str, dict[str, str]] = {
    "en->ja": {"GPU": "GPU", "latency": "レイテンシ"},
    "en->es": {"GPU": "GPU", "latency": "latencia"},
}


def apply_glossary(text: str, key: str) -> str:
    """Apply simple glossary substitutions."""
    out = text
    for src, tgt in DEFAULT_GLOSSARY.get(key, {}).items():
        out = out.replace(src, tgt)
    return out
