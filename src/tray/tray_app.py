"""System tray entrypoint."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

from src.core.database import get_connection, get_user_config, upsert_user_config
from src.tray.language_selector import build_language_radio_menu
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
    db_path: str = "voicetranslate.db"

    def run(self) -> None:
        """Run tray icon main loop."""
        self.manager.start_monitoring()
        monitor = StatusMonitor(db_path=self.db_path, poll_interval_s=5.0)
        monitor.start()
        conn = get_connection(self.db_path)

        state = {
            "source_lang": get_user_config(conn, "source_lang", "en") or "en",
            "target_lang": get_user_config(conn, "target_lang", "ja") or "ja",
            "display_lang": get_user_config(conn, "display_lang", "en") or "en",
            "tts_voice": get_user_config(conn, "tts_voice", "af_heart") or "af_heart",
        }

        icon = pystray.Icon("VoiceTranslate", _icon_image(), "VoiceTranslate")

        def persist(key: str, value: str) -> None:
            state[key] = value
            upsert_user_config(conn, key, value)
            icon.update_menu()

        def start_outgoing() -> None:
            self.manager.start(
                "outgoing",
                [
                    sys.executable,
                    "-m",
                    "src.main",
                    "run-outgoing",
                    "--source-lang",
                    str(state["source_lang"]),
                    "--target-lang",
                    str(state["target_lang"]),
                ],
            )

        def toggle_outgoing(_: pystray.Icon, __: pystray.MenuItem) -> None:
            if self.manager.is_running("outgoing"):
                self.manager.stop("outgoing")
            else:
                start_outgoing()
            icon.update_menu()

        def start_incoming() -> None:
            self.manager.start(
                "incoming",
                [
                    sys.executable,
                    "-m",
                    "src.main",
                    "run-incoming",
                    "--target-lang",
                    str(state["display_lang"]),
                ],
            )

        def toggle_incoming(_: pystray.Icon, __: pystray.MenuItem) -> None:
            if self.manager.is_running("incoming"):
                self.manager.stop("incoming")
            else:
                start_incoming()
            icon.update_menu()

        def open_control_panel(_: pystray.Icon, __: pystray.MenuItem) -> None:
            subprocess.Popen(
                [sys.executable, "-m", "src.main", "control-panel"], env=os.environ.copy()
            )

        def open_enrollment(_: pystray.Icon, __: pystray.MenuItem) -> None:
            subprocess.Popen([sys.executable, "-m", "src.main", "enroll"], env=os.environ.copy())

        def train_local(_: pystray.Icon, __: pystray.MenuItem) -> None:
            subprocess.Popen([sys.executable, "-m", "src.main", "train", "--mode", "local"])

        def train_colab(_: pystray.Icon, __: pystray.MenuItem) -> None:
            subprocess.Popen([sys.executable, "-m", "src.main", "train", "--mode", "colab"])

        def open_settings(_: pystray.Icon, __: pystray.MenuItem) -> None:
            config_path = Path("configs\\base.yaml").resolve()
            system = platform.system().lower()
            if system == "windows":
                os.startfile(config_path)  # type: ignore[attr-defined]
                return
            opener = "open" if system == "darwin" else "xdg-open"
            subprocess.Popen([opener, str(config_path)])

        def do_quit(_: pystray.Icon, __: pystray.MenuItem) -> None:
            monitor.stop()
            self.manager.stop_all()
            conn.close()
            icon.stop()

        def overall_status(_: pystray.MenuItem) -> str:
            on = self.manager.is_running("outgoing") or self.manager.is_running("incoming")
            return f"Status: {'● Active' if on else '○ Stopped'}"

        def gpu_status(_: pystray.MenuItem) -> str:
            snap = monitor.snapshot()
            vram_free = int(float(snap.get("vram_free_mb", 0.0)))
            gpu_temp = int(float(snap.get("gpu_temp_c", 0.0)))
            used = max(0, 4000 - vram_free)
            return f"GPU: {gpu_temp}°C  {used}/4000MB"

        def latency_status(_: pystray.MenuItem) -> str:
            snap = monitor.snapshot()
            return f"Latency: {float(snap['latency_ms']):.0f}ms avg"

        source_menu = build_language_radio_menu(
            current_code=lambda: str(state["source_lang"]),
            on_select=lambda code: persist("source_lang", code),
        )
        target_menu = build_language_radio_menu(
            current_code=lambda: str(state["target_lang"]),
            on_select=lambda code: persist("target_lang", code),
        )
        display_menu = build_language_radio_menu(
            current_code=lambda: str(state["display_lang"]),
            on_select=lambda code: persist("display_lang", code),
        )

        def select_voice(_: pystray.Icon, __: pystray.MenuItem, voice: str) -> None:
            persist("tts_voice", voice)

        incoming_voice_menu = pystray.Menu(
            pystray.MenuItem(
                "af_heart",
                lambda i, item: select_voice(i, item, "af_heart"),
                checked=lambda _: state["tts_voice"] == "af_heart",
                radio=True,
            ),
            pystray.MenuItem(
                "am_michael",
                lambda i, item: select_voice(i, item, "am_michael"),
                checked=lambda _: state["tts_voice"] == "am_michael",
                radio=True,
            ),
        )

        icon.menu = pystray.Menu(
            pystray.MenuItem(overall_status, lambda *_: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Outgoing Translation",
                pystray.Menu(
                    pystray.MenuItem("Source Language", source_menu),
                    pystray.MenuItem("Target Language", target_menu),
                    pystray.MenuItem(
                        lambda _: "Toggle (On)"
                        if self.manager.is_running("outgoing")
                        else "Toggle (Off)",
                        toggle_outgoing,
                    ),
                ),
            ),
            pystray.MenuItem(
                "Incoming Captions",
                pystray.Menu(
                    pystray.MenuItem("Display Language", display_menu),
                    pystray.MenuItem("TTS Voice", incoming_voice_menu),
                    pystray.MenuItem(
                        lambda _: "Toggle (On)"
                        if self.manager.is_running("incoming")
                        else "Toggle (Off)",
                        toggle_incoming,
                    ),
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Voice Enrollment...", open_enrollment),
            pystray.MenuItem(
                "Train My Voice",
                pystray.Menu(
                    pystray.MenuItem("Train Locally (RTX 3050)", train_local),
                    pystray.MenuItem("Train on Google Colab...", train_colab),
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(gpu_status, lambda *_: None, enabled=False),
            pystray.MenuItem(latency_status, lambda *_: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Control Panel", open_control_panel),
            pystray.MenuItem("Settings...", open_settings),
            pystray.MenuItem("Quit", do_quit),
        )
        icon.run()
