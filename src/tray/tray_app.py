"""System tray entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass

import pystray
from PIL import Image, ImageDraw

from src.tray.process_manager import ProcessManager
from src.tray.status_monitor import StatusMonitor


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
        self.manager.start_monitoring()
        monitor = StatusMonitor(latency_ms=620.0)
        icon = pystray.Icon("VoiceTranslate", _icon_image(), "VoiceTranslate")

        def start_outgoing() -> None:
            self.manager.start("outgoing", [sys.executable, "-m", "src.main", "run-outgoing"])

        def stop_outgoing() -> None:
            self.manager.stop("outgoing")

        def start_incoming() -> None:
            self.manager.start("incoming", [sys.executable, "-m", "src.main", "run-incoming"])

        def stop_incoming() -> None:
            self.manager.stop("incoming")

        def open_control_panel() -> None:
            subprocess.Popen(
                [sys.executable, "-m", "src.main", "control-panel"], env=os.environ.copy()
            )

        def open_enrollment() -> None:
            subprocess.Popen([sys.executable, "-m", "src.main", "enroll"], env=os.environ.copy())

        def train_local() -> None:
            subprocess.Popen([sys.executable, "-m", "src.main", "train", "--mode", "local"])

        def train_colab() -> None:
            subprocess.Popen([sys.executable, "-m", "src.main", "train", "--mode", "colab"])

        def do_quit() -> None:
            self.manager.stop_all()
            icon.stop()

        def outgoing_status(_: object) -> str:
            return f"Outgoing: {'ON' if self.manager.is_running('outgoing') else 'OFF'}"

        def incoming_status(_: object) -> str:
            return f"Incoming: {'ON' if self.manager.is_running('incoming') else 'OFF'}"

        def gpu_status(_: object) -> str:
            snap = monitor.snapshot()
            vram_free = int(float(snap.get("vram_free_mb", 0.0)))
            gpu_temp = int(float(snap.get("gpu_temp_c", 0.0)))
            used = max(0, 4000 - vram_free)
            return f"GPU: {gpu_temp}°C  {used}/4000MB"

        def latency_status(_: object) -> str:
            snap = monitor.snapshot()
            return f"Latency: {float(snap['latency_ms']):.0f}ms avg"

        icon.menu = pystray.Menu(
            pystray.MenuItem(outgoing_status, lambda: None, enabled=False),
            pystray.MenuItem(incoming_status, lambda: None, enabled=False),
            pystray.MenuItem(gpu_status, lambda: None, enabled=False),
            pystray.MenuItem(latency_status, lambda: None, enabled=False),
            pystray.MenuItem("Start Outgoing Translation", start_outgoing),
            pystray.MenuItem("Stop Outgoing Translation", stop_outgoing),
            pystray.MenuItem("Start Incoming Captions", start_incoming),
            pystray.MenuItem("Stop Incoming Captions", stop_incoming),
            pystray.MenuItem("Open Control Panel", open_control_panel),
            pystray.MenuItem("Voice Enrollment", open_enrollment),
            pystray.MenuItem("Train Locally", train_local),
            pystray.MenuItem("Train on Colab", train_colab),
            pystray.MenuItem("Quit", do_quit),
        )
        icon.run()
