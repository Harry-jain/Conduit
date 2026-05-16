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
    try:
        entries = sd.query_devices()
    except Exception:
        return devices
    for item in entries:
        devices.append(
            AudioDevice(
                name=str(item["name"]),
                max_input_channels=int(item["max_input_channels"]),
                max_output_channels=int(item["max_output_channels"]),
                samplerate=float(item["default_samplerate"]),
            )
        )
    return devices


def list_input_devices() -> list[AudioDevice]:
    """Return devices that support audio input."""
    return [dev for dev in list_audio_devices() if dev.max_input_channels > 0]


def list_output_devices() -> list[AudioDevice]:
    """Return devices that support audio output."""
    return [dev for dev in list_audio_devices() if dev.max_output_channels > 0]


def find_device_by_name(name: str) -> AudioDevice | None:
    """Find first matching device by case-insensitive substring name."""
    needle = name.strip().lower()
    if not needle:
        return None
    for dev in list_audio_devices():
        if needle in dev.name.lower():
            return dev
    return None
