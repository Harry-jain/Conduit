from src.core.config import get_config


def test_config_singleton() -> None:
    a = get_config()
    b = get_config()
    assert a is b
    assert len(a.languages.supported) == 8
