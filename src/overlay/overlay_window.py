"""Always-on-top caption overlay window."""

from __future__ import annotations

import platform
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QLabel, QWidget

from src.overlay.caption_renderer import CaptionRenderer
from src.overlay.position_calculator import position_above_taskbar
from src.platform.macos.dock_height import get_dock_height
from src.platform.windows.taskbar_height import get_taskbar_height


@dataclass
class CaptionOverlay:
    """PyQt6 overlay abstraction."""

    def __post_init__(self) -> None:
        self.renderer = CaptionRenderer()
        self.widget = QWidget()
        self.widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.label = QLabel(self.widget)
        self.label.setStyleSheet(
            "font-size: 20px;"
            "font-family: Inter, Arial, 'Noto Sans CJK JP', 'Microsoft YaHei UI', sans-serif;"
            "color: #FFFFFF;"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget.setStyleSheet("background-color: rgba(0,0,0,180);")
        self._hold_s = 3.0
        self._fade_s = 1.0
        self._fade_timer = QTimer(self.widget)
        self._fade_timer.setInterval(100)
        self._fade_timer.timeout.connect(self._tick_fade)  # type: ignore[arg-type]
        self._last_partial = ""
        self._layout_overlay()

    def show(self) -> None:
        """Show overlay."""
        self._layout_overlay()
        self.widget.show()
        self.widget.raise_()
        self.widget.setWindowOpacity(1.0)
        self._fade_timer.start()

    def hide(self) -> None:
        """Hide overlay."""
        self._fade_timer.stop()
        self.widget.hide()

    def update_partial(self, text: str) -> None:
        """Update partial text."""
        self._last_partial = text
        self.renderer.update_partial(text)
        self._render_text()
        self.widget.setWindowOpacity(1.0)
        self._fade_timer.start()

    def update_committed(self, text: str) -> None:
        """Update committed text."""
        self.renderer.update_committed(text)
        self._last_partial = ""
        self._render_text()
        self.widget.setWindowOpacity(1.0)
        self._fade_timer.start()

    def clear(self) -> None:
        """Clear overlay text."""
        self.renderer.committed = ""
        self.renderer.partial = ""
        self._last_partial = ""
        self.label.setText("")
        self.widget.setWindowOpacity(0.0)

    def set_target_language(self, lang: str) -> None:
        """Set target language hook for future directionality handling."""
        _ = lang

    def _layout_overlay(self) -> None:
        """Position overlay above taskbar/dock for primary screen."""
        app = QGuiApplication.instance()
        if app is None or app.primaryScreen() is None:
            return
        screen = app.primaryScreen()
        geo = screen.availableGeometry()
        screen_geo = screen.geometry()
        screen_w = int(screen_geo.width())
        screen_h = int(screen_geo.height())
        overlay_h = 80
        system = platform.system().lower()
        if system == "windows":
            reserve_h = max(get_taskbar_height(), screen_h - int(geo.height()))
        elif system == "darwin":
            reserve_h = max(get_dock_height(), screen_h - int(geo.height()))
        else:
            reserve_h = max(screen_h - int(geo.height()), 0)
        x, y, w, h = position_above_taskbar(
            screen_width=screen_w,
            screen_height=screen_h,
            taskbar_height=max(reserve_h, 0),
            overlay_height=overlay_h,
        )
        self.widget.setGeometry(x, y, w, h)
        self.label.setGeometry(0, 0, w, h)

    def _render_text(self) -> None:
        """Render committed and volatile text using contrasting styles."""
        committed = self.renderer.committed.strip()
        partial = self._last_partial.strip()
        committed_html = f"<span style='color:#FFFFFF;'>{committed}</span>" if committed else ""
        partial_html = (
            f"<span style='color:#A0A0A0; font-style:italic;'>{partial}</span>" if partial else ""
        )
        joiner = " " if committed_html and partial_html else ""
        self.label.setText(f"{committed_html}{joiner}{partial_html}")

    def _tick_fade(self) -> None:
        """Apply hold-and-fade policy after text updates."""
        opacity = self.renderer.tick(hold_seconds=self._hold_s, fade_seconds=self._fade_s)
        self.widget.setWindowOpacity(opacity)
        if opacity <= 0.0:
            self.label.setText("")
