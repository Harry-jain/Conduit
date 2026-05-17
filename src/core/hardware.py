"""Hardware detection and runtime recommendations."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass

import psutil
import torch


@dataclass(frozen=True)
class HardwareProfile:
    gpu_available: bool
    gpu_name: str
    vram_total_mb: int
    vram_free_mb: int
    gpu_temp_celsius: int
    cpu_count: int

    @staticmethod
    def detect() -> HardwareProfile:
        """Detect host hardware profile."""
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            total_mb = int(props.total_memory / (1024 * 1024))
            free_mb = max(total_mb - 500, 0)
            name = props.name
            temp_c = 45
            with suppress(ImportError, RuntimeError, OSError):
                import pynvml  # type: ignore

                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                free_mb = int(mem.free / (1024 * 1024))
                temp_c = int(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
                pynvml.nvmlShutdown()
        else:
            total_mb = 0
            free_mb = 0
            name = "CPU"
            temp_c = 0
        return HardwareProfile(
            gpu_available=torch.cuda.is_available(),
            gpu_name=name,
            vram_total_mb=total_mb,
            vram_free_mb=free_mb,
            gpu_temp_celsius=temp_c,
            cpu_count=psutil.cpu_count(logical=True) or 1,
        )

    def recommend_mode(self) -> str:
        """Recommend runtime mode based on available resources."""
        if self.gpu_available and self.vram_free_mb > 3500:
            return "gpu"
        if self.gpu_available and self.vram_free_mb < 2000:
            return "colab"
        return "cpu"
