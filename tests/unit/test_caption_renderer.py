import time

from src.overlay.caption_renderer import CaptionRenderer


def test_caption_renderer_stability_and_fade() -> None:
    r = CaptionRenderer()
    r.update_committed("hello ")
    full = r.update_partial("world")
    assert full.startswith("hello ")
    r.last_update_ts = time.time() - 4.0
    assert r.tick() < 1.0
