"""Language selection helpers."""

from __future__ import annotations

from collections.abc import Callable

import pystray

from src.core.constants import SUPPORTED_LANGUAGES


def available_languages() -> list[tuple[str, str]]:
    """Return supported language code/name pairs."""
    return sorted(SUPPORTED_LANGUAGES.items(), key=lambda item: item[1])


def build_language_radio_menu(
    current_code: Callable[[], str],
    on_select: Callable[[str], None],
) -> pystray.Menu:
    """Build a radio submenu for supported languages."""

    items: list[pystray.MenuItem] = []

    for code, name in available_languages():

        def _action(_: pystray.Icon, __: pystray.MenuItem, c: str = code) -> None:
            on_select(c)

        def _checked(_: pystray.MenuItem, c: str = code) -> bool:
            return current_code() == c

        items.append(
            pystray.MenuItem(
                f"{name} ({code})",
                _action,
                checked=_checked,
                radio=True,
            )
        )
    return pystray.Menu(*items)
