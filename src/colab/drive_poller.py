"""Google Drive link poller."""

from __future__ import annotations

import time
from pathlib import Path

import requests


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
            return str(dest)
        time.sleep(interval_s)
    raise TimeoutError("Checkpoint was not available in the polling window.")
