from src.overlay.position_calculator import position_above_taskbar


def test_position_calculator() -> None:
    x, y, w, h = position_above_taskbar(1920, 1080, 48, 80)
    assert (x, y, w, h) == (0, 952, 1920, 80)
