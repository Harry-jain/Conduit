"""System tray entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw
import pystray

from src.tray.process_manager import ProcessManager


def _icon_image() -> Image.Image:
    image = Image.new("RGBA", (64, 64), (20, 20, 30, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((12, 12, 52, 52), fill=(0, 220, 200, 255))
    return image


@dataclass
class TrayApp:
    """System tray application orchestrator."""

    manager: ProcessManager

    def run(self) -> None:
        """Run tray icon main loop."""
        icon = pystray.Icon("VoiceTranslate", _icon_image(), "VoiceTranslate")
        icon.menu = pystray.Menu(pystray.MenuItem("Quit", lambda: icon.stop()))
        icon.run()
