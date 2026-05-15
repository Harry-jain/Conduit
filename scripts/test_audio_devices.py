"""Audio device listing script."""

from src.audio.devices import list_audio_devices


def main() -> None:
    """List detected devices."""
    devices = list_audio_devices()
    for dev in devices:
        _ = dev


if __name__ == "__main__":
    main()
