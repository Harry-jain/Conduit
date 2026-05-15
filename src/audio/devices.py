"""Audio device discovery."""

from __future__ import annotations

from dataclasses import dataclass

import sounddevice as sd


@dataclass(frozen=True)
class AudioDevice:
    name: str
    max_input_channels: int
    max_output_channels: int
    samplerate: float


def list_audio_devices() -> list[AudioDevice]:
    """Return all audio devices visible to sounddevice."""
    devices = []
    for item in sd.query_devices():
        devices.append(
            AudioDevice(
                name=str(item["name"]),
                max_input_channels=int(item["max_input_channels"]),
                max_output_channels=int(item["max_output_channels"]),
                samplerate=float(item["default_samplerate"]),
            )
        )
    return devices
