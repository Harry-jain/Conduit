"""Colab launcher utility."""

from __future__ import annotations

import webbrowser


def open_colab(url: str) -> bool:
    """Open Colab URL in system browser."""
    return webbrowser.open(url)
