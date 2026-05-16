# Conduit Instructions (From Scratch)

This file explains the full workflow: setup, recording, training, and final usage.

## 1. Prerequisites

1. Python 3.11.x
2. Windows 11 or macOS 14
3. Optional GPU acceleration:
   - NVIDIA + CUDA-compatible driver for local GPU training/inference
4. Virtual audio device:
   - Windows: VB-Audio Virtual Cable
   - macOS: BlackHole 2ch

## 2. Fresh Setup

1. Open terminal in project root:
   - `D:\Conduit-root\Conduit`
2. Create virtual environment:
   - `python -m venv .venv`
3. Activate virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install dependencies:
   - `pip install -e ".[dev]"`
5. Create env file:
   - Windows: `copy .env.example .env`
   - macOS/Linux: `cp .env.example .env`
6. Set device names in `.env`:
   - `VOICETRANSLATE_MIC_DEVICE`
   - `VOICETRANSLATE_LOOPBACK_DEVICE`
   - `VOICETRANSLATE_VIRTUAL_MIC_DEVICE`
   - `VOICETRANSLATE_DEVICE=cuda` (or `cpu`)

## 3. Verify Audio Devices

1. Run:
   - `python scripts/test_audio_devices.py`
2. Confirm your microphone, speaker/loopback, and virtual mic appear.

## 4. Recording (Enrollment)

1. Start recording workflow:
   - `python -m src.main enroll`
2. Read all enrollment sentences clearly (60 total).
3. Output files are saved in:
   - `data/enrollment/segment_001.wav` ... `segment_060.wav`
   - `data/enrollment/segment_001_mel.npy` ... `segment_060_mel.npy`
   - `data/enrollment/metadata.json`
4. Recommended quality:
   - Quiet room
   - Stable mouth-to-mic distance
   - No clipping

## 5. Training

### A) Local training (GPU/CPU)

1. Run:
   - `python -m src.main train --mode local`
2. Checkpoints are written to:
   - `models/lora/checkpoint_<epoch>_<step>.safetensors`
   - `models/lora/latest.safetensors`

### B) Colab training

1. Generate notebook:
   - `python -m src.main train --mode colab`
2. Open:
   - `colab/train_lora.ipynb`
3. In Colab:
   - Select GPU runtime
   - Run cells in order
   - Upload training data when prompted
4. Bring produced checkpoint back to:
   - `models/lora/latest.safetensors`

## 6. Start App and Services

### Control panel mode (recommended)

1. Open control panel:
   - `python -m src.main control-panel`
2. Select mic and output devices.
3. Click:
   - **Start Outgoing** (your voice -> translated virtual mic output)
   - **Start Incoming** (incoming audio -> translated captions/audio)
4. Use stop buttons when needed.

### Tray mode

1. Run:
   - `python -m src.main run`
2. Use tray menu to start/stop services, open control panel, run enrollment/training, and quit.

## 7. Final Usage in Browser/App (Zoom, Teams, Meet)

1. In system/app audio settings, set microphone to virtual mic:
   - Windows: `CABLE Input (VB-Audio Virtual Cable)`
   - macOS: `BlackHole 2ch`
2. Keep Conduit outgoing service running.
3. Speak into your selected physical mic.
4. Verify app input meter is receiving virtual mic output.

## 8. Best Practices for Voice Cloning Quality

1. Record all 60 sentences with clean pronunciation.
2. Avoid room echo and fan noise.
3. Keep recording levels moderate (avoid clipping).
4. Retrain after collecting additional clean samples.
5. Prefer GPU mode for better training speed and consistency.

## 9. Quick Health Checks

1. Unit tests:
   - `python -m pytest tests\unit -q`
2. Integration tests:
   - `python -m pytest tests\integration -q`
3. Lint:
   - `python -m ruff check src tests`
4. Type check:
   - `python -m mypy src --ignore-missing-imports`
