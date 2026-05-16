# Setup

## Prerequisites

1. Python 3.11.x
2. Windows 11 or macOS 14
3. For NVIDIA acceleration: CUDA-capable driver (Windows)
4. VB-Audio Virtual Cable (Windows) or BlackHole 2ch (macOS)

## Installation

1. Create virtual environment:
   - `python -m venv .venv`
2. Activate:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -e ".[dev]"`
4. Copy env file:
   - Windows: `copy .env.example .env`
   - macOS/Linux: `cp .env.example .env`
5. Configure `.env` for microphone/loopback/virtual mic device names.

## Validation

1. Verify device detection:
   - `python scripts/test_audio_devices.py`
2. Run tests:
   - `python -m pytest tests\unit -q`
   - `python -m pytest tests\integration -q`
3. Run lint/type checks:
   - `python -m ruff check src tests`
   - `python -m mypy src --ignore-missing-imports`
