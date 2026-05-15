"""Always-on-top caption overlay window."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget

from src.overlay.caption_renderer import CaptionRenderer


@dataclass
class CaptionOverlay:
    """PyQt6 overlay abstraction."""

    def __post_init__(self) -> None:
        self.renderer = CaptionRenderer()
        self.widget = QWidget()
        self.widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool
        )
        self.widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.label = QLabel(self.widget)
        self.label.setStyleSheet("color: #FFFFFF; font: 20px Arial;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget.setStyleSheet("background-color: rgba(0,0,0,180);")

    def show(self) -> None:
        """Show overlay."""
        self.widget.show()

    def hide(self) -> None:
        """Hide overlay."""
        self.widget.hide()

    def update_partial(self, text: str) -> None:
        """Update partial text."""
        self.label.setText(self.renderer.update_partial(text))

    def update_committed(self, text: str) -> None:
        """Update committed text."""
        self.label.setText(self.renderer.update_committed(text))

    def clear(self) -> None:
        """Clear overlay text."""
        self.label.setText("")

    def set_target_language(self, lang: str) -> None:
        """Set target language hook for future directionality handling."""
        _ = lang
