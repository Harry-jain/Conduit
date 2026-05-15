"""VoiceTranslate CLI entrypoint."""

from __future__ import annotations

import typer

from src.core.logger import setup_logger
from src.tray.process_manager import ProcessManager
from src.tray.tray_app import TrayApp

app = typer.Typer(help="VoiceTranslate command line interface.")


@app.command()
def run() -> None:
    """Start tray daemon."""
    setup_logger()
    TrayApp(manager=ProcessManager()).run()


@app.command()
def enroll() -> None:
    """Launch enrollment mode."""
    setup_logger()


@app.command()
def train(mode: str = "local") -> None:
    """Launch training mode."""
    setup_logger()
    _ = mode


if __name__ == "__main__":
    app()
