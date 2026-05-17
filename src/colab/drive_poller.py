"""Google Drive link poller."""

from __future__ import annotations

import time
import zipfile
from pathlib import Path

import requests


def _validate_checkpoint(path: Path) -> bool:
    """Return True when checkpoint looks usable."""
    if path.suffix not in {".safetensors", ".pt", ".pth", ".bin", ".zip"}:
        return False
    return path.exists() and path.stat().st_size > 1024


def poll_and_download(
    url: str, destination: str, interval_s: int = 30, max_checks: int = 10
) -> str:
    """Poll URL and download checkpoint when available."""
    dest = Path(destination)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(max_checks):
        if not url:
            time.sleep(interval_s)
            continue
        resp = requests.get(url, timeout=30)
        if resp.ok and resp.content:
            dest.write_bytes(resp.content)
            if dest.suffix == ".zip":
                with zipfile.ZipFile(dest) as zf:
                    for member in zf.namelist():
                        if member.endswith(".safetensors"):
                            out_path = dest.with_name(Path(member).name)
                            out_path.write_bytes(zf.read(member))
                            if _validate_checkpoint(out_path):
                                return str(out_path)
            if _validate_checkpoint(dest):
                return str(dest)
        time.sleep(interval_s)
    raise TimeoutError("Checkpoint was not available in the polling window.")
