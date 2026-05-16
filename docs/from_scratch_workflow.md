# Conduit From-Scratch Workflow (Exact Method)

This is the exact operational path for collecting voice data, training, and running translation with app/browser-compatible audio routing.

## 1. Required runtime and kernels

1. **Local laptop mode**
   - Python: 3.11.x
   - CUDA: 12.2 compatible driver (for NVIDIA GPU training/inference)
   - Torch runtime: `torch==2.3.1`, `torchaudio==2.3.1`
   - OS audio stack:
     - Windows: WASAPI + VB-Audio Virtual Cable
     - macOS: CoreAudio + BlackHole 2ch
2. **Colab mode**
   - Runtime type: GPU (T4/A100 recommended)
   - Notebook kernel: Python 3 (Colab default)
   - Install from generated notebook cells (already baked by `src.colab.notebook_generator`)

## 2. Fresh setup

1. Open terminal in project root (`D:\Conduit-root\Conduit`).
2. Create and activate virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
3. Install dependencies:
   - `pip install -e ".[dev]"`
4. Copy env file:
   - `copy .env.example .env` (Windows) or `cp .env.example .env`
5. Configure `.env`:
   - `VOICETRANSLATE_MIC_DEVICE`
   - `VOICETRANSLATE_LOOPBACK_DEVICE`
   - `VOICETRANSLATE_VIRTUAL_MIC_DEVICE`
   - `VOICETRANSLATE_DEVICE=cuda` (or `cpu`)

## 3. Audio collection and storage format

1. Launch enrollment:
   - `python -m src.main enroll`
2. Enrollment corpus:
   - 60 complex sentences from `src/enrollment/sentence_corpus.py`
3. Captured data format:
   - Raw speech segment: `data/enrollment/segment_XXX.wav` (or `.flac` if configured)
   - Mel features: `data/enrollment/segment_XXX_mel.npy`
   - Metadata: `data/enrollment/metadata.json`
4. Recording quality gates:
   - Duration target: 3s to 30s
   - SNR threshold: >= 15 dB
   - Clipping threshold: < 1%

## 4. Trainer path A: local GPU / CPU

1. Ensure enrollment data exists in `data/enrollment` and training pairs are prepared in `data/training`.
2. Run local training:
   - `python -m src.main train --mode local`
3. Runtime selection:
   - GPU auto-used when `VOICETRANSLATE_DEVICE=cuda` and CUDA is available
   - CPU fallback used automatically otherwise
4. Checkpoints written to:
   - `models/lora/checkpoint_<epoch>_<step>.safetensors`
   - latest symlink/copy: `models/lora/latest.safetensors`

## 5. Trainer path B: Colab from VSCode

1. Generate notebook:
   - `python -m src.main train --mode colab`
2. Open generated notebook:
   - `colab/train_lora.ipynb` (from VSCode or browser)
3. In Colab:
   - switch runtime to GPU
   - run all cells in order
   - upload training zip when prompted
4. Download/export checkpoint and place it at:
   - `models/lora/latest.safetensors`

## 6. User UI: microphone/speaker/device selection and start/stop

1. Open desktop control UI:
   - `python -m src.main control-panel`
2. In panel:
   - Select **Input Microphone**
   - Select **Output Speaker/Loopback**
   - Click **Start Outgoing** to start outgoing speech translation
   - Click **Start Incoming** to start incoming caption+translation service
   - Stop either service independently
3. Tray mode:
   - `python -m src.main run`
   - Tray menu can start/stop outgoing and incoming services and open control panel

## 7. Browser/app compatibility (Zoom/Teams/Meet/Browser tools)

1. Configure system/app input mic to:
   - Windows: `CABLE Input (VB-Audio Virtual Cable)`
   - macOS: `BlackHole 2ch` (as virtual mic path)
2. Configure Conduit output env:
   - `VOICETRANSLATE_VIRTUAL_MIC_DEVICE` to the same virtual mic sink device
3. In conferencing app:
   - set microphone input to virtual mic device
   - verify level meter activity while Conduit outgoing service is running

## 8. Start/stop operational sequence

1. Start tray or control panel.
2. Start outgoing service.
3. Start incoming service (optional).
4. Join browser/app meeting and choose virtual mic.
5. Stop services from tray/control panel when finished.

## 9. Practical best-quality cloning checklist

1. Record in a quiet room with consistent mic distance.
2. Keep gain moderate (avoid clipping).
3. Complete all 60 sentences with clear articulation.
4. Train with GPU when possible.
5. Re-train after adding more clean enrollment segments for better speaker similarity.

---

If anything fails, first verify device names in `.env` and re-run:
- `python scripts/test_audio_devices.py`
- `python -m src.main control-panel`
