# VoiceTranslate — Claude Code Agent Instructions
# ═══════════════════════════════════════════════════════════════════════════════
# READ THIS ENTIRE FILE BEFORE WRITING A SINGLE LINE OF CODE.
# This is the authoritative specification. Every module, every file, every
# interface contract, and every acceptance criterion is defined here.
# Deviation from this spec without explicit reasoning is a failure condition.
# ═══════════════════════════════════════════════════════════════════════════════

---

## §1 — PROJECT IDENTITY

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PROJECT IDENTITY                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Project Name:    voicetranslate
Version:         0.1.0
Type:            Desktop ML Application + Background Service + OS Overlay
Scale Target:    Production-Ready (single user, local hardware)
License:         MIT

Purpose:
  A real-time, personalized speech translation desktop system that:
  (A) Records and learns the user's voice via a full-screen guided enrollment UI,
  (B) Trains a speaker-adapted TTS model on a local GPU (RTX 3050) or Google Colab,
  (C) Translates the user's outgoing speech into any of 8 supported languages
      in the user's own cloned voice and injects it as a virtual microphone,
  (D) Captures incoming meeting audio from the browser, translates it to the
      user's preferred language using a generic TTS voice, and displays real-time
      captions in an OS-level overlay above the taskbar (Windows) or menu bar
      (macOS), with NO separate voice cloning for incoming speakers.

Supported Languages (EXACTLY THESE 8, no others):
  Spanish (es) | English (en) | Japanese (ja) | German (de)
  Italian (it) | French (fr)  | Russian (ru)  | Hindi (hi)

Primary Users:
  Harsh Mukesh Jain — single-user, self-hosted, local hardware

Hard Constraints:
  - Runs 100% offline in production (no cloud APIs in inference mode)
  - Training uses LOCAL GPU (RTX 3050, 4GB VRAM) with optional Google Colab offload
  - After model generation: NO frontend required — only tensor loading + inference
  - Incoming speaker translation uses generic TTS — no voice cloning for others
  - Caption overlay must be OS-native (above taskbar Windows, above dock macOS)
  - No paid API dependencies in production inference
  - All audio data stays on-device
  - Python 3.11+ only
  - The enrollment UI is FULL SCREEN and captures the entire laptop display

Out of Scope (DO NOT BUILD):
  - Web-based UI or SaaS backend
  - Real-time video processing
  - Speaker diarization (multi-speaker identification)
  - Languages other than the 8 listed above
  - Cloud model hosting or serving
  - Mobile application
```

---

## §2 — TECH STACK MANIFEST

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  TECH STACK MANIFEST                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Runtime Environment:
  OS:              Windows 11 (primary) + macOS 14 Sonoma (secondary)
  Runtime:         Python 3.11.9
  Package Manager: pip + pyproject.toml (PEP 517)
  GPU:             NVIDIA RTX 3050 Mobile (4GB GDDR6, CUDA 12.2)
  CPU:             Intel Core i5-12th Gen (Alder Lake, 12 cores)
  RAM:             16 GB DDR5

Production Dependencies:
┌─────────────────────────────────────┬──────────────┬──────────────────────────────────────────┐
│ Package                             │ Version      │ Purpose                                  │
├─────────────────────────────────────┼──────────────┼──────────────────────────────────────────┤
│ torch                               │ ==2.3.1+cu121│ Deep learning inference + LoRA training  │
│ torchaudio                          │ ==2.3.1      │ Audio processing + mel spectrogram utils │
│ faster-whisper                      │ ==1.0.3      │ CTranslate2-based INT8 ASR (streaming)   │
│ ctranslate2                         │ ==4.3.1      │ INT8 inference runtime for Whisper+NLLB  │
│ transformers                        │ ==4.43.3     │ NLLB-200 MT model loading + tokenizer    │
│ peft                                │ ==0.12.0     │ LoRA adapter for TTS fine-tuning         │
│ librosa                             │ ==0.10.2     │ STFT, mel filterbanks, MFCC extraction   │
│ sounddevice                         │ ==0.4.7      │ Cross-platform audio capture + playback  │
│ soundfile                           │ ==0.12.1     │ WAV read/write for enrollment recordings │
│ numpy                               │ ==1.26.4     │ Signal processing arrays                 │
│ scipy                               │ ==1.13.1     │ FFT, resampling, signal utilities        │
│ PyQt6                               │ ==6.7.1      │ Full-screen enrollment UI + system tray  │
│ pyaudio                             │ ==0.2.14     │ Low-level audio stream management        │
│ silero-vad                          │ ==5.1.2      │ Voice Activity Detection (CPU, real-time) │
│ pyworld                             │ ==0.3.4      │ F0 extraction + WORLD vocoder            │
│ resemblyzer                         │ ==0.1.4      │ GE2E speaker embedding (d-vector)        │
│ noisereduce                         │ ==3.0.2      │ Spectral noise suppression pre-ASR       │
│ pynvml                              │ ==11.5.0     │ GPU temperature + utilisation monitoring │
│ psutil                              │ ==6.0.0      │ CPU utilisation monitoring for scheduler │
│ schedule                            │ ==1.2.2      │ Background training job scheduler        │
│ CosyVoice                           │ [from GitHub]│ Zero-shot TTS + streaming inference      │
│ onnxruntime-gpu                     │ ==1.18.1     │ ONNX inference for Kokoro-82M (fallback) │
│ sentencepiece                       │ ==0.2.0      │ NLLB-200 tokenizer backend               │
│ sacremoses                          │ ==0.1.1      │ Text tokenization for MT preprocessing   │
│ langdetect                          │ ==1.0.9      │ Auto-detect incoming speaker language    │
│ pystray                             │ ==0.19.5     │ System tray icon (Windows + macOS)       │
│ Pillow                              │ ==10.4.0     │ System tray icon image rendering         │
│ pywin32                             │ ==306        │ WASAPI audio session API (Windows only)  │
│ comtypes                            │ ==1.4.5      │ Windows COM interface for audio routing  │
│ requests                            │ ==2.32.3     │ Model download + Colab webhook callbacks │
│ huggingface-hub                     │ ==0.24.5     │ Model download from HuggingFace Hub      │
│ omegaconf                           │ ==2.3.0      │ YAML config management                   │
│ rich                                │ ==13.7.1     │ CLI progress bars for training           │
│ loguru                              │ ==0.7.2      │ Structured application logging           │
│ typer                               │ ==0.12.3     │ CLI entry points for all subcommands     │
├─────────────────────────────────────┼──────────────┼──────────────────────────────────────────┤
│ pytest                              │ ==8.3.2      │ Unit + integration testing framework     │
│ pytest-asyncio                      │ ==0.23.8     │ Async test support                       │
│ pytest-mock                         │ ==3.14.0     │ Mock/stub for audio device tests         │
│ ruff                                │ ==0.5.5      │ Linting + formatting                     │
│ mypy                                │ ==1.11.1     │ Static type checking                     │
│ coverage                            │ ==7.6.0      │ Test coverage reporting                  │
└─────────────────────────────────────┴──────────────┴──────────────────────────────────────────┘

ML Models (downloaded automatically on first run):
┌─────────────────────────────────────────────┬──────────────────────────────────────────┐
│ Model                                       │ Role + VRAM                              │
├─────────────────────────────────────────────┼──────────────────────────────────────────┤
│ faster-whisper base (INT8, CTranslate2)     │ ASR outgoing speech — ~620 MB VRAM       │
│ faster-whisper base (INT8, CTranslate2)     │ ASR incoming browser audio — CPU mode    │
│ NLLB-200-distilled-600M (INT8, CT2)         │ MT all 8 languages — ~1.2 GB VRAM        │
│ CosyVoice2-0.5B (FP16)                     │ TTS outgoing (user's cloned voice)       │
│ Kokoro-82M (ONNX, CPU)                     │ TTS incoming (generic voice, CPU)        │
│ Silero VAD v5                               │ Voice activity detection — CPU           │
│ GE2E Speaker Encoder (resemblyzer)          │ 256-dim speaker embedding extraction     │
│ LoRA Adapter (trained by system)            │ User voice fine-tune — <50 MB on disk    │
└─────────────────────────────────────────────┴──────────────────────────────────────────┘

VRAM Budget (RTX 3050, 4GB):
  Faster-Whisper base INT8:    620 MB
  NLLB-200-distilled-600M:    1,210 MB
  CosyVoice2-0.5B FP16:       1,480 MB
  CUDA runtime + KV cache:      200 MB
  Buffers + activations:         90 MB
  ─────────────────────────────────────
  TOTAL:                      ~3,600 MB  (400 MB headroom)

Google Colab Training:
  Framework:    PyTorch 2.3 + PEFT 0.12
  Runtime:      T4 or A100 GPU on Colab
  Upload:       Training data ZIP via gdown or google.colab.files
  Download:     LoRA checkpoint .safetensors via gdown + Drive link
  Entry point:  colab/train_lora.ipynb — self-contained notebook
```

---

## §3 — ARCHITECTURE OVERVIEW

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ARCHITECTURE OVERVIEW                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Pattern: Event-driven pipeline with three independent service processes:
  1. enrollment_service  — full-screen PyQt6 UI for voice capture + model training
  2. translate_service   — background daemon: outgoing voice translation pipeline
  3. caption_service     — background daemon: incoming audio caption + translation

Each service runs as a separate Python process communicating via:
  - Shared SQLite database (voicetranslate.db) for config + state
  - Shared filesystem for audio buffers, model checkpoints
  - IPC via localhost UDP sockets for real-time audio status events

═══════════════════════════════════════
SYSTEM A: VOICE ENROLLMENT + TRAINING
═══════════════════════════════════════

[User opens enrollment app]
        │
        ▼
[PyQt6 Full-Screen Window]
  - Takes ENTIRE screen (no taskbar, no dock visible)
  - Displays enrollment sentence (one at a time, large centered text)
  - Animated waveform visualizer showing live microphone input
  - "Say this sentence. Say DONE when finished."
  - Sentences are COMPLEX (covering all phonemes across 8 languages)
        │  User reads sentence aloud
        ▼
[VAD Detector] — detects "DONE" keyword using keyword spotting (Silero)
        │  Speech segment captured
        ▼
[Audio Validator] — checks duration (3–30s), SNR (>15dB), clipping
        │  Valid segment
        ▼
[STFT Pipeline] — extracts mel spectrogram + MFCC + F0 + speaker embedding
        │
        ▼
[Data Store] — saves mel target + metadata to data/enrollment/
        │  After 30+ sentences (~5–10 minutes of speech)
        ▼
[Training Launcher] — presents choice: LOCAL GPU or GOOGLE COLAB
        │
        ├──[LOCAL] → LoRA trainer runs on RTX 3050 (background process)
        │               → saves checkpoint to models/lora/latest.safetensors
        │
        └──[COLAB] → packages data ZIP, generates colab/train_lora.ipynb
                      → opens Google Colab in browser
                      → waits for user to paste Google Drive download link
                      → downloads checkpoint automatically

═══════════════════════════════════════
SYSTEM B: OUTGOING VOICE TRANSLATION
═══════════════════════════════════════

[Physical Microphone]  (WASAPI exclusive mode)
        │  16kHz PCM, 32ms frames
        ▼
[Silero VAD]  →  silence discarded
        │  voiced frames
        ▼
[RNNoise Denoiser]  →  background noise removed
        │
        ▼
[Faster-Whisper base INT8]  →  streaming partial transcripts (GPU)
        │  committed tokens (Wait-k=4)
        ▼  ┌─────────────────────────────────────┐
[NLLB-600M INT8]  ←  target language from config  (GPU)
        │  translated text chunks
        ▼
[CosyVoice2-0.5B]  ←  user's speaker_embedding.npy  (GPU)
  + LoRA adapter   ←  models/lora/latest.safetensors
        │  synthesized 22kHz audio chunks (20ms each)
        ▼
[VB-Audio Virtual Cable]  (Windows) / [BlackHole] (macOS)
        │  injected as virtual microphone
        ▼
[Zoom / Teams / Google Meet sees "VoiceTranslate Mic"]

═══════════════════════════════════════
SYSTEM C: INCOMING CAPTION + TRANSLATION
═══════════════════════════════════════

[Browser Audio Output]  (WASAPI loopback / BlackHole)
  ← What the user HEARS from the meeting (Japanese, German, etc.)
        │  48kHz stereo, captured as system audio
        ▼
[Resampler] → 16kHz mono
        ▼
[Silero VAD]  →  silence discarded
        │
        ▼
[langdetect]  →  auto-detects incoming language
        │
        ▼
[Faster-Whisper base INT8]  (CPU mode, does NOT use GPU)
        │  transcribed text in source language
        ▼
[NLLB-600M INT8]  →  translates to user's preferred language  (GPU shared)
        │  English (or preferred) text
        ▼ ─────────────────────────────────────────────────────────
        │                                                           │
        ▼                                                           ▼
[Caption Overlay]                                     [Kokoro-82M TTS]  (CPU)
  OS-level always-on-top window                         Generic voice output
  Bottom-center of screen                               Plays through speakers
  Above taskbar (Windows)                               (user hears translation)
  Above dock (macOS)
  Text scrolls left-to-right
  Prefix-stability algorithm (no flicker)

Key Architectural Decisions:
  1. THREE SEPARATE PROCESSES: Enrollment, OutgoingTranslation, CaptionService
     run as independent Python processes. Crashes in one do not kill others.
     Orchestrated by the system tray daemon (src/tray/tray_app.py).

  2. GPU SHARED BETWEEN OUTGOING + INCOMING: NLLB-600M is loaded once and
     shared between both translation directions via a request queue (asyncio).
     GPU is NOT shared with incoming ASR — that runs on CPU to avoid VRAM pressure.

  3. NO VOICE CLONING FOR INCOMING: Kokoro-82M uses a fixed pre-trained speaker
     profile (professional male/female selectable) for translating incoming speech.
     This saves 1.5GB VRAM vs loading CosyVoice2 for incoming direction.

  4. LORA ADAPTER HOT-SWAP: The TTS engine checks models/lora/latest.safetensors
     every 60 seconds. If the file is newer than the loaded version, it reloads
     the adapter without restarting the TTS process.

  5. COLAB TRAINING: The Colab notebook is self-contained — it installs all deps,
     loads training data from a ZIP, trains, and uploads the checkpoint to Google
     Drive. The local app polls for a Drive share link and downloads automatically.

  6. CAPTION OVERLAY IS OS-NATIVE: On Windows, uses WS_EX_TOOLWINDOW +
     HWND_TOPMOST + SetWindowPos. On macOS, NSPanel with NSFloatingWindowLevel.
     The overlay has zero chrome — just semi-transparent black bar with white text.
     Position: horizontal center, Y = screen_height - taskbar_height - overlay_height.

What is explicitly NOT in this architecture:
  - No web server, no REST API, no WebSockets between components
  - No database server (SQLite only, single file)
  - No Docker (desktop app, not containerised)
  - No frontend framework (PyQt6 for enrollment only; overlay is raw OS window)
  - No cloud inference in production mode
  - No speaker diarization
```

---

## §4 — COMPLETE FILE TREE

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  COMPLETE FILE TREE                                                          ║
║  Total: ~120 files across 28 directories                                     ║
║  Every file listed MUST exist. Do not skip, rename, or combine.             ║
╚══════════════════════════════════════════════════════════════════════════════╝

voicetranslate/                                  # Project root
│
├── CLAUDE.md                                    # This file (agent instructions)
├── README.md                                    # User-facing setup + usage guide
├── CHANGELOG.md                                 # Version history
├── LICENSE                                      # MIT license text
├── pyproject.toml                               # Package config + all deps with pins
├── Makefile                                     # All dev commands (setup, test, run, train)
├── .gitignore                                   # Python + models + audio data ignores
├── .env.example                                 # All env vars documented
├── .ruff.toml                                   # Ruff linter + formatter config
├── mypy.ini                                     # MyPy type checker config
├── pytest.ini                                   # Pytest config + markers
│
├── configs/                                     # All YAML configs (OmegaConf)
│   ├── base.yaml                                # Master config (inherits all below)
│   ├── languages.yaml                           # 8 language codes, names, NLLB tags
│   ├── audio.yaml                               # Sample rates, buffer sizes, VAD params
│   ├── models.yaml                              # Model paths, VRAM limits, quantization
│   ├── training.yaml                            # LoRA rank, LR, batch size, epochs
│   ├── enrollment.yaml                          # Sentences list, recording params
│   ├── overlay.yaml                             # Caption position, font, colors, timing
│   └── colab.yaml                               # Colab export settings, Drive poll interval
│
├── src/                                         # All application source code
│   │
│   ├── __init__.py
│   ├── main.py                                  # Entry point: launches tray daemon
│   │
│   ├── core/                                    # Shared utilities (no UI, no audio)
│   │   ├── __init__.py
│   │   ├── config.py                            # OmegaConf loader, env var injection
│   │   ├── logger.py                            # Loguru setup, log rotation, level config
│   │   ├── database.py                          # SQLite connection, schema creation
│   │   ├── exceptions.py                        # Custom exception hierarchy
│   │   ├── constants.py                         # LANGUAGES dict, SAMPLE_RATE, CHUNK_SIZE
│   │   └── hardware.py                          # GPU detection, VRAM query, CPU core count
│   │
│   ├── audio/                                   # Low-level audio I/O
│   │   ├── __init__.py
│   │   ├── capture.py                           # Microphone capture (WASAPI exclusive mode)
│   │   ├── loopback.py                          # System audio loopback capture (browser audio)
│   │   ├── virtual_mic.py                       # VB-Audio / BlackHole virtual mic writer
│   │   ├── resampler.py                         # Sample rate conversion (libsamplerate)
│   │   ├── vad.py                               # Silero VAD wrapper, frame-level detection
│   │   ├── denoiser.py                          # RNNoise spectral denoiser wrapper
│   │   ├── validator.py                         # SNR check, clipping check, duration check
│   │   └── devices.py                           # List + select audio devices cross-platform
│   │
│   ├── signal/                                  # Fourier + speaker identity processing
│   │   ├── __init__.py
│   │   ├── stft.py                              # STFT, inverse STFT, mel spectrogram
│   │   ├── mfcc.py                              # MFCC extraction, delta, delta-delta
│   │   ├── f0.py                                # WORLD-based F0 extraction via pyworld
│   │   ├── formants.py                          # LPC formant analysis (F1–F4)
│   │   ├── speaker_encoder.py                   # GE2E d-vector via resemblyzer
│   │   └── embedding_store.py                   # Save/load speaker_embedding.npy
│   │
│   ├── models/                                  # ML model loaders + inference wrappers
│   │   ├── __init__.py
│   │   ├── downloader.py                        # HuggingFace Hub auto-download on first run
│   │   ├── asr/
│   │   │   ├── __init__.py
│   │   │   ├── whisper_gpu.py                   # Faster-Whisper GPU streaming (outgoing ASR)
│   │   │   └── whisper_cpu.py                   # Faster-Whisper CPU (incoming ASR)
│   │   ├── mt/
│   │   │   ├── __init__.py
│   │   │   ├── nllb_engine.py                   # NLLB-200-distilled-600M CTranslate2 engine
│   │   │   ├── wait_k.py                        # Wait-k=4 prefix-to-prefix streaming policy
│   │   │   ├── language_detect.py               # langdetect wrapper for incoming audio
│   │   │   └── glossary.py                      # Domain-specific term constrained decoding
│   │   ├── tts/
│   │   │   ├── __init__.py
│   │   │   ├── cosyvoice_engine.py              # CosyVoice2-0.5B streaming inference
│   │   │   ├── kokoro_engine.py                 # Kokoro-82M ONNX generic voice (incoming)
│   │   │   ├── lora_loader.py                   # LoRA adapter hot-swap + checkpoint watcher
│   │   │   └── vocoder.py                       # HiFi-GAN waveform generation (shared)
│   │   └── vad/
│   │       ├── __init__.py
│   │       └── silero_vad.py                    # Silero VAD v5 frame classifier
│   │
│   ├── pipeline/                                # Async processing pipelines
│   │   ├── __init__.py
│   │   ├── outgoing_pipeline.py                 # Mic→VAD→ASR→MT→TTS→VirtualMic (async)
│   │   ├── incoming_pipeline.py                 # Loopback→VAD→ASR→MT→Caption+TTS (async)
│   │   ├── queue_manager.py                     # asyncio Queue wrappers for inter-stage comms
│   │   └── pipeline_metrics.py                  # Latency tracking per stage, health monitor
│   │
│   ├── enrollment/                              # Voice enrollment system (System A)
│   │   ├── __init__.py
│   │   ├── sentence_corpus.py                   # Complex sentence list for all 8 languages
│   │   ├── session_manager.py                   # Enrollment session state, progress tracking
│   │   ├── keyword_spotter.py                   # "DONE" keyword detection via Silero
│   │   ├── recording_engine.py                  # Segment capture, validation, file save
│   │   └── data_packager.py                     # ZIP packager for Colab upload
│   │
│   ├── training/                                # LoRA training (local GPU mode)
│   │   ├── __init__.py
│   │   ├── lora_trainer.py                      # PEFT LoRA training loop for CosyVoice2
│   │   ├── dataset.py                           # PyTorch Dataset: (mel_input, mel_target) pairs
│   │   ├── dataloader.py                        # DataLoader factory, train/val split
│   │   ├── optimizer.py                         # AdamW with cosine LR scheduler
│   │   ├── callbacks.py                         # EarlyStopping, ModelCheckpoint, MetricLogger
│   │   ├── metrics.py                           # MCD + SECS quality gate computation
│   │   ├── checkpoint_manager.py                # Save/load/rollback safetensors checkpoints
│   │   └── idle_scheduler.py                    # Background idle detector + training trigger
│   │
│   ├── colab/                                   # Google Colab integration
│   │   ├── __init__.py
│   │   ├── notebook_generator.py                # Generates train_lora.ipynb programmatically
│   │   ├── drive_poller.py                      # Polls for Drive share link + downloads checkpoint
│   │   └── colab_launcher.py                    # Opens Colab in system browser
│   │
│   ├── overlay/                                 # Caption overlay (System C display)
│   │   ├── __init__.py
│   │   ├── overlay_window.py                    # OS-native always-on-top window (PyQt6)
│   │   ├── caption_renderer.py                  # Text rendering, prefix-stability, scroll
│   │   ├── position_calculator.py               # Taskbar height detection, overlay placement
│   │   └── theme.py                             # Colors, fonts, opacity settings
│   │
│   ├── tray/                                    # System tray daemon (main process)
│   │   ├── __init__.py
│   │   ├── tray_app.py                          # pystray icon + menu, process orchestrator
│   │   ├── process_manager.py                   # Subprocess launch/kill/monitor for 3 services
│   │   ├── language_selector.py                 # Tray submenu: source + target language choice
│   │   └── status_monitor.py                    # GPU temp, latency, pipeline health display
│   │
│   └── platform/                                # OS-specific implementations
│       ├── __init__.py
│       ├── windows/
│       │   ├── __init__.py
│       │   ├── wasapi_capture.py                # WASAPI exclusive-mode mic via pywin32
│       │   ├── wasapi_loopback.py               # WASAPI loopback for browser audio
│       │   ├── virtual_cable.py                 # VB-Audio Virtual Cable writer
│       │   ├── overlay_win.py                   # Win32 HWND_TOPMOST overlay positioning
│       │   └── taskbar_height.py                # Query Windows taskbar height via Shell API
│       └── macos/
│           ├── __init__.py
│           ├── coreaudio_capture.py             # CoreAudio mic capture via sounddevice
│           ├── blackhole_capture.py             # BlackHole loopback for browser audio
│           ├── virtual_cable.py                 # BlackHole virtual mic writer
│           ├── overlay_mac.py                   # NSPanel NSFloatingWindowLevel overlay
│           └── dock_height.py                   # Query macOS dock height + position
│
├── colab/                                       # Google Colab training notebook (generated)
│   ├── train_lora.ipynb                         # [AUTO-GENERATED by notebook_generator.py]
│   └── colab_requirements.txt                   # Pinned deps for Colab environment
│
├── data/                                        # All runtime data (gitignored)
│   ├── enrollment/                              # Recorded voice segments (.wav + .npy mel)
│   │   └── .gitkeep
│   ├── training/                                # Processed training pairs for LoRA
│   │   └── .gitkeep
│   └── exports/                                 # ZIP archives for Colab upload
│       └── .gitkeep
│
├── models/                                      # Downloaded + trained models (gitignored)
│   ├── whisper/                                 # Faster-Whisper base INT8
│   │   └── .gitkeep
│   ├── nllb/                                    # NLLB-200-distilled-600M CTranslate2
│   │   └── .gitkeep
│   ├── cosyvoice/                               # CosyVoice2-0.5B weights
│   │   └── .gitkeep
│   ├── kokoro/                                  # Kokoro-82M ONNX
│   │   └── .gitkeep
│   ├── speaker/                                 # speaker_embedding.npy (user's d-vector)
│   │   └── .gitkeep
│   └── lora/                                    # LoRA adapter checkpoints
│       └── .gitkeep
│
├── logs/                                        # Runtime logs (gitignored)
│   └── .gitkeep
│
├── scripts/                                     # Utility scripts
│   ├── setup.sh                                 # One-command dev environment setup (Linux/macOS)
│   ├── setup.bat                                # One-command dev environment setup (Windows)
│   ├── download_models.py                       # Pre-download all ML models
│   ├── install_vb_cable.bat                     # Silent VB-Audio install (Windows)
│   ├── install_blackhole.sh                     # BlackHole install instructions (macOS)
│   ├── test_audio_devices.py                    # Verify mic + virtual cable detected
│   └── benchmark_latency.py                     # End-to-end pipeline latency benchmark
│
├── tests/                                       # Test suite
│   ├── conftest.py                              # Shared fixtures: mock audio, config, DB
│   ├── fixtures/
│   │   ├── sample_audio_16k.wav                 # 3s test audio at 16kHz
│   │   ├── sample_audio_22k.wav                 # 3s test audio at 22kHz
│   │   └── sample_embedding.npy                 # Pre-computed speaker embedding
│   ├── unit/
│   │   ├── test_config.py                       # Config loading + env var injection
│   │   ├── test_stft.py                         # STFT output shapes + mel spectrogram
│   │   ├── test_mfcc.py                         # MFCC extraction, delta computation
│   │   ├── test_f0.py                           # F0 extraction on voiced/unvoiced frames
│   │   ├── test_speaker_encoder.py              # Embedding shape (256,), cosine similarity
│   │   ├── test_vad.py                          # VAD detects speech/silence correctly
│   │   ├── test_denoiser.py                     # Denoiser output shape + SNR improvement
│   │   ├── test_validator.py                    # Validator rejects clipped/short/noisy audio
│   │   ├── test_wait_k.py                       # Wait-k emits k tokens before sentence end
│   │   ├── test_nllb_engine.py                  # NLLB translates 8-language pairs (mocked)
│   │   ├── test_lora_trainer.py                 # LoRA loss decreases over 2 steps
│   │   ├── test_metrics.py                      # MCD + SECS computed correctly
│   │   ├── test_checkpoint_manager.py           # Save/load/rollback checkpoint
│   │   ├── test_sentence_corpus.py              # Corpus has ≥30 sentences, all 8 langs covered
│   │   ├── test_caption_renderer.py             # Prefix-stability: no full string replacement
│   │   └── test_position_calculator.py          # Overlay position above taskbar
│   └── integration/
│       ├── conftest.py                          # Integration test fixtures (real audio devices)
│       ├── test_outgoing_pipeline.py            # Full outgoing pipeline mock-to-mock
│       └── test_incoming_pipeline.py            # Full incoming pipeline mock-to-caption
│
└── docs/
    ├── architecture.md                          # System design, data flow diagrams
    ├── setup.md                                 # Step-by-step local setup guide
    ├── enrollment_guide.md                      # How to use enrollment UI
    ├── training_guide.md                        # Local vs Colab training instructions
    ├── audio_routing.md                         # VB-Audio + BlackHole setup instructions
    └── languages.md                             # Supported languages + NLLB language codes
```

---

## §5 — MODULE SPECIFICATIONS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  MODULE SPECIFICATIONS                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Module: core/config.py
**Purpose**: Load, validate, and expose all application configuration from YAML + env vars.
**Location**: `src/core/config.py`
**Dependencies**: omegaconf==2.3.0, python-dotenv==1.0.1

**Interface Contract**:
```python
from src.core.config import get_config, Config

cfg = get_config()  # Singleton — loads once, cached

# All fields typed:
cfg.audio.sample_rate        # int = 16000
cfg.audio.chunk_size_ms      # int = 32
cfg.models.whisper_path      # str = "models/whisper/"
cfg.training.lora_rank       # int = 8
cfg.training.learning_rate   # float = 1e-4
cfg.languages.supported      # List[str] = ["en","es","ja","de","it","fr","ru","hi"]
cfg.overlay.height_px        # int = 80
cfg.overlay.font_size        # int = 20
```

**Acceptance Criteria**:
- [ ] `get_config()` returns identical object on repeated calls (singleton)
- [ ] Raises `ConfigValidationError` if required field is missing
- [ ] Env vars in `.env` override YAML values (e.g., `VOICETRANSLATE_MODELS_PATH`)
- [ ] All 8 language codes validated against `constants.SUPPORTED_LANGUAGES`
- [ ] No raw `os.environ` calls anywhere else in the codebase

---

### Module: core/hardware.py
**Purpose**: Detect GPU availability, query VRAM, determine which model variants to load.
**Location**: `src/core/hardware.py`
**Dependencies**: pynvml==11.5.0, torch==2.3.1

**Interface Contract**:
```python
from src.core.hardware import HardwareProfile

hw = HardwareProfile.detect()
hw.gpu_available        # bool
hw.gpu_name             # str = "NVIDIA GeForce RTX 3050 Laptop GPU"
hw.vram_total_mb        # int = 4096
hw.vram_free_mb         # int = ~3600 at startup
hw.gpu_temp_celsius     # int — real-time query
hw.cpu_count            # int = 12
hw.recommend_mode()     # -> "gpu" | "cpu" | "colab"
```

**Acceptance Criteria**:
- [ ] Returns correct VRAM figure from pynvml
- [ ] `recommend_mode()` returns `"gpu"` when vram_free > 3500 MB
- [ ] `recommend_mode()` returns `"cpu"` when no GPU or vram_free < 2000 MB
- [ ] GPU temperature queried without blocking (non-blocking NVML call)

---

### Module: audio/capture.py
**Purpose**: Capture microphone audio via WASAPI exclusive mode (Windows) or CoreAudio (macOS).
**Location**: `src/audio/capture.py`
**Dependencies**: pyaudio==0.2.14, sounddevice==0.4.7

**Interface Contract**:
```python
from src.audio.capture import MicrophoneCapture

cap = MicrophoneCapture(
    device_name="Headset Microphone",  # or None for default
    sample_rate=16000,
    chunk_ms=32,                       # 512 samples @ 16kHz
    exclusive_mode=True                # Windows WASAPI exclusive
)

cap.start()
for chunk in cap.stream():            # Generator, blocks until chunk ready
    # chunk: np.ndarray shape (512,), dtype float32, range [-1, 1]
    process(chunk)
cap.stop()
```

**Acceptance Criteria**:
- [ ] Captures audio at exactly 16000 Hz (resamples if device uses different rate)
- [ ] Exclusive mode reduces buffer latency to ≤10ms on Windows
- [ ] Falls back to shared mode gracefully if exclusive mode unavailable
- [ ] `cap.stop()` cleanly closes the audio stream without ResourceWarning
- [ ] Cross-platform: uses `platform_selector` to call correct backend

---

### Module: audio/loopback.py
**Purpose**: Capture system audio output (browser meeting audio) for incoming translation.
**Location**: `src/audio/loopback.py`
**Dependencies**: pyaudio==0.2.14, sounddevice==0.4.7

**Interface Contract**:
```python
from src.audio.loopback import SystemLoopbackCapture

lb = SystemLoopbackCapture(
    target_device="Speakers",  # or "BlackHole 2ch" on macOS
    sample_rate=48000,
    chunk_ms=32,
)

lb.start()
for chunk in lb.stream():  # stereo float32 → auto-downmixed to mono
    # chunk: np.ndarray shape (1536,) = 32ms at 48kHz
    process(chunk)
lb.stop()
```

**Acceptance Criteria**:
- [ ] Windows: uses WASAPI loopback (not exclusive) — AUDCLNT_STREAMFLAGS_LOOPBACK
- [ ] macOS: uses BlackHole 2ch virtual device as loopback source
- [ ] Stereo input automatically converted to mono (average channels)
- [ ] Does NOT capture VoiceTranslate's own output (channel isolation documented in code comment)

---

### Module: audio/virtual_mic.py
**Purpose**: Write translated synthesized audio to virtual microphone buffer.
**Location**: `src/audio/virtual_mic.py`
**Dependencies**: sounddevice==0.4.7, pyaudio==0.2.14

**Interface Contract**:
```python
from src.audio.virtual_mic import VirtualMicWriter

vmw = VirtualMicWriter(
    device_name="CABLE Input (VB-Audio Virtual Cable)",  # Windows
    # or "BlackHole 2ch" on macOS
    sample_rate=22050,
    buffer_ms=20,
)

vmw.open()
vmw.write(audio_chunk_float32)  # np.ndarray shape (N,), range [-1,1]
vmw.close()
```

**Acceptance Criteria**:
- [ ] Audio plays through to meeting app at correct sample rate
- [ ] Buffer underruns log a WARNING but do not raise exceptions
- [ ] `write()` is non-blocking (puts chunk in internal ring buffer)
- [ ] Works with Zoom, Teams, Google Meet (verified by listing virtual mic in their audio settings)

---

### Module: audio/vad.py
**Purpose**: Frame-level voice activity detection using Silero VAD v5.
**Location**: `src/audio/vad.py`
**Dependencies**: silero-vad==5.1.2, torch==2.3.1

**Interface Contract**:
```python
from src.audio.vad import VADDetector

vad = VADDetector(
    sample_rate=16000,
    threshold=0.5,
    min_speech_duration_ms=250,
    min_silence_duration_ms=300,  # Silence duration to trigger segment boundary
)

result = vad.process(chunk_float32)
# result.is_speech: bool
# result.probability: float [0,1]
# result.segment_complete: bool — True when silence follows speech
```

**Acceptance Criteria**:
- [ ] Runs on CPU only (never loads to GPU)
- [ ] Processes 32ms frames in <2ms wall-clock time on i5-12th Gen
- [ ] `segment_complete=True` when 300ms silence follows ≥250ms speech
- [ ] Speech probability logged to metrics pipeline every 100 frames

---

### Module: signal/stft.py
**Purpose**: Compute STFT, mel spectrogram, and inverse STFT for voice processing.
**Location**: `src/signal/stft.py`
**Dependencies**: librosa==0.10.2, numpy==1.26.4, torchaudio==2.3.1

**Interface Contract**:
```python
from src.signal.stft import STFTPipeline

stft = STFTPipeline(
    sample_rate=22050,
    n_fft=1024,
    hop_length=256,
    win_length=1024,
    n_mels=80,
    fmin=80,
    fmax=8000,
)

mel = stft.audio_to_mel(audio_np)
# mel: np.ndarray shape (80, T), log-compressed, range ~[-11.5, 2.0]

audio = stft.mel_to_audio(mel)
# audio: np.ndarray shape (N,), float32, range [-1,1]

stft_mag, stft_phase = stft.audio_to_stft(audio_np)
# stft_mag: shape (513, T)  stft_phase: shape (513, T)
```

**Acceptance Criteria**:
- [ ] `audio_to_mel(audio_to_mel_inverse(x))` round-trips within 2 dB MCD
- [ ] Output shape (80, T) where T = ceil(len(audio) / hop_length)
- [ ] No NaN or Inf values in output for valid audio input
- [ ] Processes 10s of audio in < 50ms on CPU (librosa vectorised)

---

### Module: signal/speaker_encoder.py
**Purpose**: Extract 256-dim GE2E speaker embedding from mel spectrogram.
**Location**: `src/signal/speaker_encoder.py`
**Dependencies**: resemblyzer==0.1.4, numpy==1.26.4

**Interface Contract**:
```python
from src.signal.speaker_encoder import SpeakerEncoder

enc = SpeakerEncoder()  # Loads pretrained GE2E weights from resemblyzer

embedding = enc.embed_audio(audio_np_16k)
# embedding: np.ndarray shape (256,), L2-normalized, range [-1,1]

embedding = enc.embed_utterances(list_of_audio_arrays)
# Returns centroid embedding of all utterances — used for enrollment

similarity = enc.cosine_similarity(emb_a, emb_b)
# float: range [-1,1], >0.85 = same speaker threshold
```

**Acceptance Criteria**:
- [ ] Embedding shape is exactly (256,)
- [ ] L2 norm of embedding == 1.0 (normalized)
- [ ] Same speaker utterances: cosine_similarity > 0.85
- [ ] Different speaker utterances: cosine_similarity < 0.70
- [ ] Runs on CPU in < 100ms for 10s audio

---

### Module: enrollment/sentence_corpus.py
**Purpose**: Provide the list of complex phonetically-balanced enrollment sentences.
**Location**: `src/enrollment/sentence_corpus.py`
**Dependencies**: None (pure Python)

**CRITICAL REQUIREMENTS for sentences**:
- Minimum 60 sentences total
- Each sentence 15–30 words long (long enough to be complex)
- Phonetically balanced: must cover all vowels, consonants, and phoneme clusters
- Include technical vocabulary (covers jitter and intonation patterns)
- Include questions, statements, and exclamations (covers pitch variation)
- Include numbers, acronyms, and foreign-sounding words (stress patterns)
- Must NOT include profanity, sensitive topics, or personally identifying info
- The "DONE" keyword (spoken, not written) triggers segment completion

**Interface Contract**:
```python
from src.enrollment.sentence_corpus import SentenceCorpus

corpus = SentenceCorpus()
sentence = corpus.next()           # Returns next sentence string
corpus.current_index               # int: which sentence we're on
corpus.total_count                 # int: 60
corpus.is_complete                 # bool: all sentences done
corpus.reset()                     # Start from beginning
corpus.get_random(n=5)             # List[str]: random selection
```

**Sample sentences (implement ALL 60, these are examples)**:
```
1. "The extraordinary complexity of modern artificial intelligence systems 
    requires sophisticated mathematical foundations in linear algebra and calculus."

2. "Quantum computing architectures leverage superposition and entanglement 
    to solve optimization problems that classical computers cannot address efficiently."

3. "Seventeen biochemical pathways regulate cellular respiration in eukaryotic 
    organisms, each requiring specific enzymatic cofactors and precise pH balance."

4. "The philosophical implications of machine consciousness remain thoroughly 
    unresolved despite decades of rigorous academic debate among cognitive scientists."

5. "Sophisticated neural network architectures achieve remarkable performance 
    on benchmark datasets by exploiting hierarchical feature representations."

[... continue for all 60 sentences covering all English phoneme clusters ...]
```

**Acceptance Criteria**:
- [ ] `len(corpus.get_all()) == 60`
- [ ] Every sentence ≥ 15 words
- [ ] Phoneme coverage analysis: all 44 English phonemes present across corpus
- [ ] No duplicate sentences
- [ ] `next()` raises `StopIteration` after all 60 sentences used

---

### Module: enrollment/keyword_spotter.py
**Purpose**: Detect when the user says the word "DONE" to end a recording segment.
**Location**: `src/enrollment/keyword_spotter.py`
**Dependencies**: faster-whisper==1.0.3

**Implementation Strategy**:
Use Faster-Whisper Tiny model in streaming mode on CPU to transcribe every 1-second
window of incoming audio. If the transcription contains "done", "DONE", "done.", or
"Done" in the last 3 tokens, fire the segment_complete event.

**Interface Contract**:
```python
from src.enrollment.keyword_spotter import KeywordSpotter

ks = KeywordSpotter(keyword="done", confidence_threshold=0.7)

ks.start_listening()

for audio_chunk in mic_stream:
    result = ks.process(audio_chunk)
    if result.keyword_detected:
        # User said "DONE" — stop recording current segment
        stop_recording()
        break
```

**Acceptance Criteria**:
- [ ] Detects "done" within 500ms of utterance
- [ ] False positive rate < 5% on held-out audio without keyword
- [ ] Works regardless of sentence content preceding "done"
- [ ] Runs on CPU (Whisper Tiny model, <200ms latency)

---

### Module: enrollment/recording_engine.py
**Purpose**: Orchestrate the full enrollment recording loop for one sentence.
**Location**: `src/enrollment/recording_engine.py`

**Interface Contract**:
```python
from src.enrollment.recording_engine import RecordingEngine, RecordingResult

engine = RecordingEngine(config=cfg.enrollment)

result: RecordingResult = engine.record_sentence(sentence_text="...")
# result.audio_np: np.ndarray — speech segment (DONE keyword stripped)
# result.duration_s: float — duration of recorded speech
# result.snr_db: float — measured SNR
# result.was_clipped: bool
# result.mel_spectrogram: np.ndarray shape (80, T)
# result.accepted: bool — passes all validation checks
# result.rejection_reason: str | None
```

**Acceptance Criteria**:
- [ ] Recording starts exactly when user begins speaking (VAD-gated)
- [ ] "DONE" keyword stripped from end of recording before saving
- [ ] Segment rejected if SNR < 15 dB, duration < 3s, or clipping detected
- [ ] Mel spectrogram computed and saved alongside WAV file
- [ ] Each segment saved as: `data/enrollment/segment_{index:03d}.wav`
- [ ] Metadata saved as: `data/enrollment/metadata.json`

---

### Module: enrollment UI (src/enrollment/ui.py — PyQt6)
**Purpose**: Full-screen enrollment user interface.
**Location**: `src/enrollment/ui.py`
**Dependencies**: PyQt6==6.7.1

**CRITICAL UI REQUIREMENTS**:
- Window takes ENTIRE screen — `showFullScreen()`, no window decorations
- Background: solid dark color (#1a1a2e)
- Sentence text: white, centered, font-size 42px, max-width 80% of screen width
- Word-by-word highlight: as user speaks, recognized words highlight in cyan
- Waveform visualizer: animated real-time waveform at bottom 20% of screen
- Progress bar: thin horizontal bar at top showing sentence X of 60
- Status text: "Say this sentence. Say DONE when finished." — below sentence
- Instruction text: smaller, gray, at bottom explaining the process
- Press ESC to pause enrollment and return to tray menu
- After sentence recorded + accepted: brief ✓ animation, advance to next sentence
- After sentence rejected: "Let's try again." message + same sentence re-shown

**Interface Contract**:
```python
from src.enrollment.ui import EnrollmentWindow

win = EnrollmentWindow(corpus=sentence_corpus, engine=recording_engine)
win.start()                          # Shows full screen
win.signals.sentence_complete        # pyqtSignal emitted per accepted sentence
win.signals.enrollment_complete      # pyqtSignal when all 60 done
win.signals.training_requested       # pyqtSignal(mode) where mode = "local"|"colab"
```

**Acceptance Criteria**:
- [ ] Window covers 100% of screen including taskbar area on Windows
- [ ] No application title bar, no close/minimize/maximize buttons visible
- [ ] Waveform updates at 60 FPS using QTimer
- [ ] Text wraps correctly for sentences > screen width
- [ ] ESC key pauses and shows tray menu without killing the process
- [ ] Training mode selection dialog appears after 30+ sentences recorded

---

### Module: training/lora_trainer.py
**Purpose**: Train a LoRA adapter on CosyVoice2-0.5B using enrolled voice data.
**Location**: `src/training/lora_trainer.py`
**Dependencies**: peft==0.12.0, torch==2.3.1, transformers==4.43.3

**LoRA Configuration**:
```python
lora_config = LoraConfig(
    r=8,                                    # Rank — 8 for voice adaptation
    lora_alpha=16,                          # Scaling: alpha/r = 2.0
    target_modules=["q_proj", "v_proj"],    # Attention projections only
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
# Trainable params: ~2.1M / 500M total = 0.42%
# Additional VRAM during training: ~8 MB
```

**Interface Contract**:
```python
from src.training.lora_trainer import LoRATrainer

trainer = LoRATrainer(
    base_model_path="models/cosyvoice/",
    speaker_embedding=np.load("models/speaker/speaker_embedding.npy"),
    data_dir="data/training/",
    checkpoint_dir="models/lora/",
    config=cfg.training,
    device="cuda",                          # or "cpu" for Colab fallback
)

history = trainer.train()
# history.train_loss:  List[float] per epoch
# history.val_loss:    List[float] per epoch
# history.mcd_scores:  List[float] — Mel Cepstral Distortion per checkpoint
# history.secs_scores: List[float] — Speaker Encoder Cosine Similarity
# history.best_checkpoint: str — path to best accepted checkpoint

trainer.train_step()  # Single step — for idle scheduler incremental training
```

**Training Loop**:
```
For each epoch:
  1. Sample (mel_input, speaker_embedding, mel_target) from DataLoader
  2. CosyVoice2 forward pass with LoRA adapter active
  3. Compute mel reconstruction loss (L1 loss on log-mel spectrogram)
  4. Backward pass — only LoRA parameters receive gradients
  5. AdamW step with cosine LR schedule
  6. Every 50 steps: compute MCD on validation set
  7. Every 100 steps: compute SECS on 10 held-out utterances
  8. Accept checkpoint if MCD < 6.0 dB AND SECS > 0.85
  9. Reject + rollback if quality gates fail
```

**Acceptance Criteria**:
- [ ] Training loss decreases over first 100 steps (verified on smoke test with tiny batch)
- [ ] Checkpoint saved as `models/lora/checkpoint_{epoch}_{step}.safetensors`
- [ ] Best checkpoint symlinked to `models/lora/latest.safetensors`
- [ ] SECS improves from ~0.72 (epoch 0) toward ≥0.85 (epoch 10+) with 30min data
- [ ] Training on RTX 3050 uses ≤8MB additional VRAM above inference stack
- [ ] Gradient clipping applied (max_norm=1.0)
- [ ] Mixed precision (FP16) enabled via torch.cuda.amp.autocast
- [ ] Ctrl+C stops training cleanly and saves current checkpoint

---

### Module: training/idle_scheduler.py
**Purpose**: Monitor GPU + CPU utilisation and trigger incremental LoRA training during idle periods.
**Location**: `src/training/idle_scheduler.py`
**Dependencies**: pynvml==11.5.0, psutil==6.0.0, schedule==1.2.2

**Interface Contract**:
```python
from src.training.idle_scheduler import IdleScheduler

scheduler = IdleScheduler(
    gpu_util_threshold=30,          # % — start training below this
    cpu_util_threshold=40,          # % — start training below this
    gpu_temp_threshold=80,          # °C — never train above this
    idle_timeout_minutes=5,         # Must be idle this long before training starts
    check_interval_seconds=30,      # How often to check utilisation
)

scheduler.start()  # Runs in background thread
scheduler.stop()
scheduler.status   # "idle_waiting" | "training" | "paused_hot" | "stopped"
```

**Acceptance Criteria**:
- [ ] Training starts only after GPU+CPU both below threshold for ≥5 minutes
- [ ] Training stops immediately when GPU util rises above threshold
- [ ] Training never starts if GPU temp ≥ 80°C
- [ ] Each training run is logged with start time, duration, steps completed
- [ ] Scheduler survives GPU driver query failures (non-fatal exception handling)

---

### Module: colab/notebook_generator.py
**Purpose**: Generate a self-contained Colab notebook that trains the LoRA adapter.
**Location**: `src/colab/notebook_generator.py`
**Dependencies**: nbformat==5.10.4

**Notebook must contain these cells (in order)**:
```
Cell 1: Runtime check — verify T4/A100 GPU is available
Cell 2: Install dependencies — torch, peft, transformers, torchaudio
Cell 3: Mount Google Drive for checkpoint output
Cell 4: Upload training data — from local ZIP (google.colab.files.upload())
Cell 5: Extract ZIP to /content/training_data/
Cell 6: Load CosyVoice2-0.5B base model from HuggingFace
Cell 7: Apply LoRA config (same config as local training)
Cell 8: Training loop — 20 epochs, progress bar with rich
Cell 9: Save checkpoint to Google Drive /MyDrive/voicetranslate/lora_checkpoint.safetensors
Cell 10: Print shareable Google Drive link to checkpoint
```

**Interface Contract**:
```python
from src.colab.notebook_generator import ColabNotebookGenerator

gen = ColabNotebookGenerator(config=cfg.training)
notebook_path = gen.generate(
    output_path="colab/train_lora.ipynb",
    training_data_zip="data/exports/training_data.zip",
)
# Returns: Path to generated .ipynb file
```

**Acceptance Criteria**:
- [ ] Generated notebook is valid JSON (nbformat.validate passes)
- [ ] All cells have correct cell_type ("code" or "markdown")
- [ ] No hardcoded paths — all paths use Colab-standard `/content/` prefix
- [ ] Checkpoint file is saved with timestamp in filename
- [ ] Final cell prints a clickable download link

---

### Module: models/asr/whisper_gpu.py
**Purpose**: Streaming ASR for outgoing speech using Faster-Whisper on GPU.
**Location**: `src/models/asr/whisper_gpu.py`
**Dependencies**: faster-whisper==1.0.3, ctranslate2==4.3.1

**Interface Contract**:
```python
from src.models.asr.whisper_gpu import WhisperGPUStreamer

asr = WhisperGPUStreamer(
    model_size="base",                  # base.en for English source
    device="cuda",
    compute_type="int8",
    language="en",                      # Source language for outgoing speech
)

asr.start_stream()

for audio_chunk in mic_stream:
    asr.feed(audio_chunk)               # Non-blocking feed
    for token in asr.get_committed_tokens():
        mt_queue.put(token)             # Wait-k: tokens flow to MT immediately

asr.stop_stream()
```

**Acceptance Criteria**:
- [ ] VRAM usage ≤ 650 MB when loaded
- [ ] Processes 32ms audio chunks with ≤120ms latency on RTX 3050
- [ ] Emits committed tokens (confidence > 0.7) as they are generated
- [ ] Handles mid-utterance language switches gracefully (no crash)

---

### Module: models/mt/nllb_engine.py
**Purpose**: Neural machine translation between all 8 supported languages.
**Location**: `src/models/mt/nllb_engine.py`
**Dependencies**: ctranslate2==4.3.1, sentencepiece==0.2.0, sacremoses==0.1.1

**Supported Language Pairs**:
```python
NLLB_LANG_CODES = {
    "en": "eng_Latn",
    "es": "spa_Latn",
    "ja": "jpn_Jpan",
    "de": "deu_Latn",
    "it": "ita_Latn",
    "fr": "fra_Latn",
    "ru": "rus_Cyrl",
    "hi": "hin_Deva",
}
# All 56 direction pairs (8×7) are supported by the same model
```

**Interface Contract**:
```python
from src.models.mt.nllb_engine import NLLBTranslator

mt = NLLBTranslator(
    model_path="models/nllb/",
    device="cuda",
    compute_type="int8",
)

# Full sentence translation
result = mt.translate(
    text="Hello, how are you?",
    source_lang="en",
    target_lang="ja",
)
# result.text: str = "こんにちは、お元気ですか？"
# result.latency_ms: float

# Streaming partial translation (Wait-k mode)
for partial_token in mt.translate_stream(
    token_stream=asr_committed_tokens,
    source_lang="en",
    target_lang="ja",
    k=4,
):
    tts_queue.put(partial_token)
```

**Acceptance Criteria**:
- [ ] VRAM usage ≤ 1,250 MB when loaded
- [ ] Translates 10-word sentence in ≤ 120ms on RTX 3050
- [ ] Supports all 56 direction pairs (8 languages × 7 targets)
- [ ] BLEU ≥ 40 on FLORES-200 en→ja pair (spot-checked, not full eval)
- [ ] Only one model instance loaded — shared between outgoing and incoming via async queue

---

### Module: models/tts/cosyvoice_engine.py
**Purpose**: Zero-shot streaming TTS for outgoing speech in the user's cloned voice.
**Location**: `src/models/tts/cosyvoice_engine.py`
**Dependencies**: CosyVoice (GitHub), torch==2.3.1

**Interface Contract**:
```python
from src.models.tts.cosyvoice_engine import CosyVoiceEngine

tts = CosyVoiceEngine(
    model_path="models/cosyvoice/",
    speaker_embedding=np.load("models/speaker/speaker_embedding.npy"),
    lora_checkpoint="models/lora/latest.safetensors",
    device="cuda",
    streaming=True,
    chunk_frames=20,                    # 20 mel frames = ~116ms audio chunks
)

for audio_chunk in tts.synthesize_stream(text="こんにちは、お元気ですか？"):
    # audio_chunk: np.ndarray shape (2560,) = ~116ms at 22050Hz
    virtual_mic.write(audio_chunk)

# TTFA (time to first audio): ≤150ms
# Subsequent chunks: generated at RTF ~0.12 (12x real-time)
```

**Acceptance Criteria**:
- [ ] VRAM usage ≤ 1,500 MB including LoRA adapter
- [ ] TTFA ≤ 150ms from first text token available
- [ ] LoRA adapter loaded from `latest.safetensors` on initialization
- [ ] LoRA adapter hot-reloaded when `latest.safetensors` mtime changes
- [ ] Synthesizes speech for all 8 supported target languages
- [ ] SECS (synthesized vs reference) ≥ 0.80 after 1 week background training

---

### Module: models/tts/kokoro_engine.py
**Purpose**: Generic-voice TTS for incoming translation (no voice cloning).
**Location**: `src/models/tts/kokoro_engine.py`
**Dependencies**: onnxruntime-gpu==1.18.1 (falls back to onnxruntime CPU)

**Interface Contract**:
```python
from src.models.tts.kokoro_engine import KokoroEngine

tts = KokoroEngine(
    model_path="models/kokoro/kokoro-v0_19.onnx",
    voice_preset="af_heart",            # Professional female English voice
    device="cpu",                       # Always CPU — GPU reserved for outgoing
    sample_rate=22050,
)

audio = tts.synthesize(text="Hello, I understand what was just said.")
# audio: np.ndarray, float32, 22050Hz
# Duration ≈ len(text)/10 seconds for natural speech rate
```

**Accepted voice presets** (user-selectable in tray menu):
- `af_heart` — English female, warm
- `am_michael` — English male, professional
- (Additional voices from Kokoro model card)

**Acceptance Criteria**:
- [ ] Runs entirely on CPU — never touches GPU
- [ ] Synthesizes 10-word sentence in ≤ 800ms on i5-12th Gen
- [ ] Output sample rate is exactly 22050 Hz
- [ ] Works for all 8 languages' translated text (text is always in user's preferred language)

---

### Module: pipeline/outgoing_pipeline.py
**Purpose**: Full async outgoing speech translation pipeline with pipeline parallelism.
**Location**: `src/pipeline/outgoing_pipeline.py`
**Dependencies**: asyncio (stdlib), all model modules

**Pipeline Parallelism Implementation**:
```python
# Three async tasks running concurrently:
# Task 1: MicCapture → VAD → denoiser → ASR_queue
# Task 2: ASR_queue  → Wait-k MT → TTS_queue (starts when k=4 tokens available)
# Task 3: TTS_queue  → CosyVoice2 → VirtualMic  (starts when first translated token)
#
# This means MT starts translating WHILE ASR is still transcribing the 5th+ word.
# TTS starts speaking WHILE MT is translating the 2nd clause.
# Total latency ≈ max(stage_latency) not sum(stage_latency).
```

**Interface Contract**:
```python
from src.pipeline.outgoing_pipeline import OutgoingTranslationPipeline

pipeline = OutgoingTranslationPipeline(
    source_lang="en",
    target_lang="ja",
    asr=whisper_gpu,
    mt=nllb_engine,
    tts=cosyvoice_engine,
    mic=mic_capture,
    virtual_mic=virtual_mic_writer,
)

await pipeline.start()          # Non-blocking, runs until stop()
await pipeline.stop()
pipeline.metrics.e2e_latency_ms # Rolling average end-to-end latency
pipeline.metrics.asr_wer_est   # Estimated WER from confidence scores
```

**Acceptance Criteria**:
- [ ] End-to-end latency (glass-to-ear): ≤ 750ms for 10-word utterances on RTX 3050
- [ ] Pipeline continues running if any single chunk fails (error logged, next chunk processed)
- [ ] MT stage begins ≤ 200ms after speech starts (Wait-k triggers on token 4)
- [ ] No echo: VirtualMic output never enters MicCapture stream

---

### Module: pipeline/incoming_pipeline.py
**Purpose**: Full async incoming caption + translation pipeline for browser audio.
**Location**: `src/pipeline/incoming_pipeline.py`

**Interface Contract**:
```python
from src.pipeline.incoming_pipeline import IncomingCaptionPipeline

pipeline = IncomingCaptionPipeline(
    target_lang="en",                   # User's preferred language for captions
    asr=whisper_cpu,                    # Always CPU — GPU reserved for outgoing
    language_detector=lang_detect,
    mt=nllb_engine,                     # Shared GPU instance via async queue
    tts=kokoro_engine,                  # Generic voice, CPU
    loopback=system_loopback,
    caption_overlay=overlay_window,
)

await pipeline.start()
await pipeline.stop()
```

**Acceptance Criteria**:
- [ ] Caption appears ≤ 500ms after incoming speech ends
- [ ] Language detection fires within first 500ms of incoming utterance
- [ ] Caption overlay updated using prefix-stability algorithm (no full-string flicker)
- [ ] Kokoro TTS audio plays through speakers (not virtual mic — that's outgoing only)
- [ ] If incoming audio is already in user's target language, MT step skipped (passed through)

---

### Module: overlay/overlay_window.py
**Purpose**: OS-native always-on-top caption overlay above the taskbar.
**Location**: `src/overlay/overlay_window.py`
**Dependencies**: PyQt6==6.7.1

**CRITICAL LAYOUT REQUIREMENTS**:
```
Windows:
  Position: x=0, y=(screen_height - taskbar_height - overlay_height)
  Width: screen_width (full width)
  Height: 80px
  Window flags: Qt.WindowType.FramelessWindowHint
              | Qt.WindowType.WindowStaysOnTopHint
              | Qt.WindowType.Tool  (does not appear in taskbar)
  Background: rgba(0, 0, 0, 180)  — semi-transparent black
  Text: white, Inter/Arial 20px, centered horizontally + vertically

macOS:
  Position: x=0, y=(screen_height - dock_height - overlay_height)
  Same width + height + styling as Windows
  NSPanel level: NSFloatingWindowLevel + 1 (above all normal windows)
  NSWindowCollectionBehavior: .canJoinAllSpaces + .stationary

Common behavior (both platforms):
  - Click-through: overlay never intercepts mouse events
  - Caption text scrolls horizontally if longer than window width
  - Prefix-stability: only update the "volatile suffix" of the caption
  - Committed (stable) text shown in bright white
  - Partial (volatile) text shown in gray, italicized
  - Caption held on screen for 3 seconds after speaker stops
  - Smooth fade-out after 3s hold (1s alpha transition)
```

**Interface Contract**:
```python
from src.overlay.overlay_window import CaptionOverlay

overlay = CaptionOverlay()
overlay.show()
overlay.hide()

overlay.update_partial(text="こんにちは")           # Volatile text (user still speaking)
overlay.update_committed(text="こんにちは、")       # Locked text (high confidence)
overlay.clear()                                    # Hide caption immediately
overlay.set_target_language(lang="en")             # Affects text direction (RTL for Arabic — not supported but hook exists)
```

**Acceptance Criteria**:
- [ ] Overlay visible above taskbar on Windows 11 with multiple monitors
- [ ] Overlay visible above dock on macOS 14 with default dock position (bottom)
- [ ] Mouse clicks pass through overlay — does not block interaction with apps below
- [ ] Overlay stays on top of all applications including fullscreen video
- [ ] Prefix-stability: committed text never disappears or reorders
- [ ] Text rendering handles Japanese CJK characters (requires CJK-compatible font)

---

### Module: tray/tray_app.py
**Purpose**: System tray icon that orchestrates all three service processes.
**Location**: `src/tray/tray_app.py`
**Dependencies**: pystray==0.19.5, Pillow==10.4.0

**Tray Menu Structure**:
```
VoiceTranslate
├── Status: ● Active / ○ Stopped
├── ─────────────────────────────
├── Outgoing Translation
│   ├── Source Language  →  [8 language submenu, radio buttons]
│   ├── Target Language  →  [8 language submenu, radio buttons]
│   └── Toggle (On/Off)
├── Incoming Captions
│   ├── Display Language →  [8 language submenu, radio buttons]
│   ├── TTS Voice        →  [af_heart / am_michael]
│   └── Toggle (On/Off)
├── ─────────────────────────────
├── Voice Enrollment...          # Opens full-screen enrollment UI
├── Train My Voice
│   ├── Train Locally (RTX 3050)
│   └── Train on Google Colab...
├── ─────────────────────────────
├── GPU Status: 45°C  3.6/4.0GB
├── Latency: 620ms avg
├── ─────────────────────────────
├── Settings...                  # Opens config YAML in default editor
└── Quit
```

**Acceptance Criteria**:
- [ ] Tray icon visible in system tray on Windows 11 and macOS 14
- [ ] Menu shows real-time GPU temperature (updates every 5s)
- [ ] Language changes take effect in running pipelines within 2s
- [ ] "Quit" cleanly terminates all three service processes
- [ ] All three services restart automatically if they crash (process monitor)

---

## §6 — DATA MODELS

```python
# src/core/database.py — SQLite schema

CREATE TABLE IF NOT EXISTS user_config (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
# Keys: source_lang, target_lang, display_lang, tts_voice, outgoing_enabled,
#       incoming_enabled, training_mode, lora_checkpoint_path

CREATE TABLE IF NOT EXISTS enrollment_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      DATETIME NOT NULL,
    completed_at    DATETIME,
    sentences_done  INTEGER DEFAULT 0,
    total_sentences INTEGER DEFAULT 60,
    status          TEXT DEFAULT 'in_progress'  -- 'in_progress'|'complete'|'abandoned'
);

CREATE TABLE IF NOT EXISTS recording_segments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER REFERENCES enrollment_sessions(id),
    sentence_index  INTEGER NOT NULL,
    sentence_text   TEXT NOT NULL,
    audio_path      TEXT NOT NULL,      -- relative: data/enrollment/segment_001.wav
    mel_path        TEXT NOT NULL,      -- relative: data/enrollment/segment_001_mel.npy
    duration_s      REAL NOT NULL,
    snr_db          REAL NOT NULL,
    accepted        BOOLEAN NOT NULL,
    rejection_reason TEXT,
    recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS training_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    mode            TEXT NOT NULL,      -- 'local'|'colab'
    started_at      DATETIME NOT NULL,
    completed_at    DATETIME,
    epochs_done     INTEGER DEFAULT 0,
    best_mcd        REAL,
    best_secs       REAL,
    checkpoint_path TEXT,
    status          TEXT DEFAULT 'running'  -- 'running'|'complete'|'failed'|'cancelled'
);

CREATE TABLE IF NOT EXISTS pipeline_metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline        TEXT NOT NULL,      -- 'outgoing'|'incoming'
    e2e_latency_ms  REAL NOT NULL,
    asr_latency_ms  REAL NOT NULL,
    mt_latency_ms   REAL NOT NULL,
    tts_latency_ms  REAL NOT NULL,
    gpu_temp_c      INTEGER,
    vram_used_mb    INTEGER,
    recorded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## §7 — CONFIGURATION FILES

### configs/languages.yaml
```yaml
supported:
  - code: en
    name: English
    nllb_code: eng_Latn
    whisper_lang: en
    tts_supported: true

  - code: es
    name: Spanish
    nllb_code: spa_Latn
    whisper_lang: es
    tts_supported: true

  - code: ja
    name: Japanese
    nllb_code: jpn_Jpan
    whisper_lang: ja
    tts_supported: true

  - code: de
    name: German
    nllb_code: deu_Latn
    whisper_lang: de
    tts_supported: true

  - code: it
    name: Italian
    nllb_code: ita_Latn
    whisper_lang: it
    tts_supported: true

  - code: fr
    name: French
    nllb_code: fra_Latn
    whisper_lang: fr
    tts_supported: true

  - code: ru
    name: Russian
    nllb_code: rus_Cyrl
    whisper_lang: ru
    tts_supported: true

  - code: hi
    name: Hindi
    nllb_code: hin_Deva
    whisper_lang: hi
    tts_supported: true

default_source: en
default_target: ja
default_display: en
```

### configs/audio.yaml
```yaml
microphone:
  sample_rate: 16000
  chunk_ms: 32
  channels: 1
  dtype: float32
  exclusive_mode: true        # WASAPI exclusive on Windows

loopback:
  sample_rate: 48000
  chunk_ms: 32
  channels: 2                 # Stereo → downmix to mono
  dtype: float32

virtual_mic:
  sample_rate: 22050
  buffer_ms: 20
  channels: 1

vad:
  threshold: 0.5
  min_speech_ms: 250
  min_silence_ms: 300         # Segment boundary after 300ms silence
  frame_ms: 32

denoiser:
  enabled: true
  stationary_noise: true
  prop_decrease: 0.9          # 90% noise reduction

enrollment:
  min_duration_s: 3.0
  max_duration_s: 30.0
  min_snr_db: 15.0
  max_clipping_pct: 0.01      # < 1% of samples at ±1.0
```

### configs/training.yaml
```yaml
lora:
  rank: 8
  alpha: 16
  target_modules:
    - q_proj
    - v_proj
  dropout: 0.05
  bias: none

optimizer:
  type: AdamW
  learning_rate: 1.0e-4
  weight_decay: 1.0e-4
  betas: [0.9, 0.999]

scheduler:
  type: cosine
  warmup_steps: 50
  min_lr: 1.0e-6

training:
  epochs: 20
  batch_size: 4
  gradient_clip: 1.0
  mixed_precision: true       # FP16 via torch.cuda.amp

quality_gates:
  min_secs: 0.85              # Speaker Encoder Cosine Similarity threshold
  max_mcd_db: 6.0             # Mel Cepstral Distortion threshold
  eval_every_n_steps: 50
  checkpoint_every_n_steps: 100

idle_scheduler:
  gpu_util_threshold: 30      # %
  cpu_util_threshold: 40      # %
  gpu_temp_threshold: 80      # °C
  idle_timeout_minutes: 5
  check_interval_seconds: 30
```

### configs/overlay.yaml
```yaml
window:
  height_px: 80
  opacity: 0.85               # 85% opaque, 15% transparent
  background_color: "#000000"
  position: bottom_center     # above taskbar/dock

typography:
  font_family: "Arial"        # Fallback if system font unavailable
  font_size_px: 20
  committed_color: "#FFFFFF"  # Bright white for confirmed text
  partial_color: "#A0A0A0"    # Gray for in-progress text
  partial_italic: true

timing:
  hold_duration_s: 3.0        # Keep caption visible for 3s after speech ends
  fade_duration_s: 1.0        # Fade out over 1s

stability:
  prefix_lock_threshold: 0.85 # Lock token when confidence > this
  max_rollback_tokens: 3      # Maximum tokens that can be updated after commitment
```

---

## §8 — ENVIRONMENT VARIABLES

### .env.example
```bash
# VoiceTranslate — Environment Configuration
# Copy to .env and fill in your values

# ─── Paths ────────────────────────────────────────────────────────────────────
VOICETRANSLATE_DATA_DIR=./data
VOICETRANSLATE_MODELS_DIR=./models
VOICETRANSLATE_LOGS_DIR=./logs

# ─── Audio Devices (auto-detected if blank) ───────────────────────────────────
VOICETRANSLATE_MIC_DEVICE=             # Leave blank for default microphone
VOICETRANSLATE_LOOPBACK_DEVICE=        # "CABLE Output" on Windows, "BlackHole 2ch" on macOS
VOICETRANSLATE_VIRTUAL_MIC_DEVICE=     # "CABLE Input" on Windows, "BlackHole 2ch" on macOS

# ─── GPU Settings ─────────────────────────────────────────────────────────────
VOICETRANSLATE_DEVICE=cuda             # cuda | cpu
VOICETRANSLATE_CUDA_DEVICE_ID=0        # GPU index (0 for primary GPU)
VOICETRANSLATE_VRAM_LIMIT_MB=3800      # Maximum VRAM to use (MB)

# ─── Training Mode ────────────────────────────────────────────────────────────
VOICETRANSLATE_TRAINING_MODE=local     # local | colab
VOICETRANSLATE_COLAB_DRIVE_LINK=       # Google Drive share link (set after Colab training)

# ─── Google Colab (only needed if training_mode=colab) ────────────────────────
VOICETRANSLATE_COLAB_POLL_INTERVAL_S=30   # How often to check for completed checkpoint

# ─── Logging ──────────────────────────────────────────────────────────────────
VOICETRANSLATE_LOG_LEVEL=INFO          # DEBUG | INFO | WARNING | ERROR
VOICETRANSLATE_LOG_ROTATION=10 MB      # Rotate logs at this size

# ─── HuggingFace (for model download) ─────────────────────────────────────────
HUGGINGFACE_HUB_TOKEN=                 # Optional, for gated models
HF_HOME=./models/hf_cache             # Local cache directory
```

---

## §9 — TESTING REQUIREMENTS

```
Testing Framework: pytest==8.3.2 + pytest-asyncio + pytest-mock
Coverage Target: ≥75% overall, ≥90% for core/ and pipeline/ modules

Test Markers:
  @pytest.mark.unit        — Pure Python, no audio devices, no GPU
  @pytest.mark.integration — Requires actual audio devices or GPU
  @pytest.mark.slow        — Takes > 30 seconds (excluded from CI fast run)

Smoke Test (runs in < 60 seconds, no GPU required):
  tests/unit/test_config.py          — Config loads without error
  tests/unit/test_stft.py            — STFT round-trip shape correct
  tests/unit/test_sentence_corpus.py — 60 sentences, all long enough
  tests/unit/test_caption_renderer.py— Prefix-stability algorithm correct

Critical Unit Tests to Implement:
  test_stft.py:
    - mel output shape is (80, T) for any valid audio input
    - Round-trip audio_to_mel → mel_to_audio within 2 dB MCD
    - No NaN/Inf in output for [-1,1] audio input
    - Handles silence (all-zeros) without error

  test_speaker_encoder.py:
    - Embedding shape == (256,)
    - L2 norm == 1.0
    - Same audio → same embedding (deterministic)
    - Different audio → different embedding (cosine_sim < 0.99)

  test_vad.py:
    - Silence frames (below threshold): is_speech == False
    - Voiced frames (above threshold): is_speech == True
    - segment_complete fires after 300ms silence

  test_wait_k.py:
    - With k=4: MT queue receives first token only after 4th ASR token
    - With k=4 and 10-word utterance: MT starts at token 4, not token 10
    - Streaming continues correctly for 20-token sequences

  test_lora_trainer.py:
    - Loss at step 2 < loss at step 0 (tiny batch overfit check)
    - Checkpoint saved to correct path
    - Only LoRA params have gradients (base model frozen)
    - Rollback: if MCD > 6.0, reverts to previous checkpoint

  test_caption_renderer.py:
    - update_partial: only tail of string changes, prefix preserved
    - update_committed: committed text never removed
    - After 3s: caption fades (opacity decreases)

  test_position_calculator.py:
    - Returns (x=0, y=correct_y) for 1920×1080 with 48px taskbar
    - Returns correct y for multiple monitor configurations
    - macOS: places above dock height
```

---

## §10 — BUILD AND RUN COMMANDS

```bash
# ═══════════════════════════════════════════════════════════════
# INITIAL SETUP (run once)
# ═══════════════════════════════════════════════════════════════

# 1. Create virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install all dependencies
pip install -e ".[dev]"

# 3. Copy environment config
cp .env.example .env
# Edit .env — set VOICETRANSLATE_MIC_DEVICE, VOICETRANSLATE_LOOPBACK_DEVICE

# 4. Download all ML models (runs automatically on first use, but run manually to pre-cache)
python scripts/download_models.py

# 5. Install VB-Audio Virtual Cable (Windows — run as administrator)
scripts\install_vb_cable.bat

# 5b. Install BlackHole (macOS)
# Follow: docs/audio_routing.md

# 6. Verify audio devices are detected correctly
python scripts/test_audio_devices.py

# ═══════════════════════════════════════════════════════════════
# DAILY COMMANDS (Makefile targets)
# ═══════════════════════════════════════════════════════════════

make run            # Start full system (tray daemon + all services)
make enroll         # Open full-screen enrollment UI directly
make train-local    # Start LoRA training on local GPU immediately
make train-colab    # Generate Colab notebook + open in browser
make test           # Run full test suite with coverage
make test-unit      # Unit tests only (fast, no GPU required)
make test-int       # Integration tests (requires audio devices)
make lint           # ruff check + ruff format --check
make format         # ruff format (auto-fix)
make typecheck      # mypy src/
make benchmark      # Run latency benchmark (scripts/benchmark_latency.py)
make download       # Download all ML models
make clean          # Remove __pycache__, .mypy_cache, .pytest_cache

# ═══════════════════════════════════════════════════════════════
# Makefile (create this exactly)
# ═══════════════════════════════════════════════════════════════

.PHONY: run enroll train-local train-colab test test-unit test-int \
        lint format typecheck benchmark download clean

run:
	python -m src.main

enroll:
	python -m src.main enroll

train-local:
	python -m src.main train --mode local

train-colab:
	python -m src.main train --mode colab

test:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing \
	       -m "not integration" -v

test-unit:
	pytest tests/unit/ -v --tb=short

test-int:
	pytest tests/integration/ -v --tb=short -m integration

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/ --ignore-missing-imports

benchmark:
	python scripts/benchmark_latency.py

download:
	python scripts/download_models.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
```

---

## §11 — AGENT INSTRUCTIONS (IMPLEMENTATION ORDER)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  AGENT INSTRUCTIONS                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

You are implementing voicetranslate from scratch.
Read this ENTIRE file before writing any code.
Follow the phases in STRICT ORDER — do not jump ahead.

═══════════════════════════════════
PHASE 0 — FOUNDATION (Days 1–2)
═══════════════════════════════════
Create ALL of these before any source code:

[ ] pyproject.toml with all dependencies and exact version pins from §2
[ ] Makefile with all targets from §10
[ ] .env.example with all variables from §8
[ ] .gitignore (Python standard + models/ + data/ + logs/ + .env)
[ ] .ruff.toml with: line-length=100, target-version="py311"
[ ] mypy.ini with: python_version=3.11, strict=false, ignore_missing_imports=true
[ ] pytest.ini with: asyncio_mode=auto, markers defined
[ ] Complete directory tree from §4 (all directories + .gitkeep files)
[ ] configs/base.yaml, configs/languages.yaml, configs/audio.yaml,
    configs/training.yaml, configs/overlay.yaml, configs/colab.yaml
[ ] docs/architecture.md, docs/setup.md stubs

Verify: `python -c "import src; print('OK')"` passes.

═══════════════════════════════════
PHASE 1 — CORE + HARDWARE (Day 2)
═══════════════════════════════════
[ ] src/core/constants.py — LANGUAGES dict, SAMPLE_RATES, CHUNK_SIZES
[ ] src/core/exceptions.py — ConfigValidationError, AudioDeviceError,
                              ModelLoadError, TrainingError, VRAMError
[ ] src/core/logger.py — Loguru setup, rotation, level from env
[ ] src/core/config.py — OmegaConf loader, singleton, env override
[ ] src/core/database.py — SQLite connection, schema creation on init
[ ] src/core/hardware.py — HardwareProfile.detect(), recommend_mode()
[ ] tests/unit/test_config.py — all acceptance criteria
Run: make test-unit — must pass.

═══════════════════════════════════
PHASE 2 — SIGNAL PROCESSING (Day 3)
═══════════════════════════════════
[ ] src/signal/stft.py — STFTPipeline with mel, inverse, stft methods
[ ] src/signal/mfcc.py — MFCC + delta + delta-delta extraction
[ ] src/signal/f0.py — WORLD F0 extraction via pyworld
[ ] src/signal/formants.py — LPC formant analysis
[ ] src/signal/speaker_encoder.py — GE2E via resemblyzer
[ ] src/signal/embedding_store.py — save/load speaker_embedding.npy
[ ] tests/unit/test_stft.py — shape, round-trip, NaN checks
[ ] tests/unit/test_mfcc.py
[ ] tests/unit/test_speaker_encoder.py
Run: make test-unit — must pass.

═══════════════════════════════════
PHASE 3 — AUDIO I/O (Days 3–4)
═══════════════════════════════════
[ ] src/platform/windows/wasapi_capture.py
[ ] src/platform/windows/wasapi_loopback.py
[ ] src/platform/windows/virtual_cable.py
[ ] src/platform/windows/overlay_win.py
[ ] src/platform/windows/taskbar_height.py
[ ] src/platform/macos/coreaudio_capture.py (stub if developing on Windows)
[ ] src/platform/macos/blackhole_capture.py (stub)
[ ] src/platform/macos/virtual_cable.py (stub)
[ ] src/platform/macos/overlay_mac.py (stub)
[ ] src/platform/macos/dock_height.py (stub)
[ ] src/audio/capture.py — platform-selecting wrapper
[ ] src/audio/loopback.py — platform-selecting wrapper
[ ] src/audio/virtual_mic.py — platform-selecting wrapper
[ ] src/audio/vad.py — Silero VAD wrapper
[ ] src/audio/denoiser.py — RNNoise wrapper
[ ] src/audio/validator.py — SNR, clipping, duration checks
[ ] src/audio/devices.py — list all audio devices
[ ] src/audio/resampler.py — sample rate conversion
[ ] tests/unit/test_vad.py
[ ] tests/unit/test_validator.py
Run: python scripts/test_audio_devices.py — verify mic detected.

═══════════════════════════════════
PHASE 4 — MODEL LOADERS (Days 4–5)
═══════════════════════════════════
[ ] src/models/downloader.py — HuggingFace Hub auto-download logic
[ ] src/models/vad/silero_vad.py — model loading + frame classification
[ ] src/models/asr/whisper_gpu.py — Faster-Whisper GPU streaming
[ ] src/models/asr/whisper_cpu.py — Faster-Whisper CPU (incoming)
[ ] src/models/mt/language_detect.py — langdetect wrapper
[ ] src/models/mt/wait_k.py — Wait-k=4 streaming policy
[ ] src/models/mt/glossary.py — constrained decoding term pairs
[ ] src/models/mt/nllb_engine.py — NLLB-200 CTranslate2 engine
[ ] src/models/tts/vocoder.py — HiFi-GAN waveform generation
[ ] src/models/tts/lora_loader.py — LoRA adapter hot-swap watcher
[ ] src/models/tts/cosyvoice_engine.py — CosyVoice2 streaming TTS
[ ] src/models/tts/kokoro_engine.py — Kokoro-82M ONNX generic TTS
[ ] tests/unit/test_wait_k.py
[ ] tests/unit/test_nllb_engine.py (mocked — no real GPU in unit tests)
Run: python scripts/download_models.py — verify all models download.
Run: python -c "from src.models.asr.whisper_gpu import WhisperGPUStreamer; m = WhisperGPUStreamer(); print('ASR OK')"

═══════════════════════════════════
PHASE 5 — ENROLLMENT SYSTEM (Days 5–6)
═══════════════════════════════════
[ ] src/enrollment/sentence_corpus.py — ALL 60 sentences implemented
[ ] src/enrollment/keyword_spotter.py — "DONE" detection via Whisper Tiny
[ ] src/enrollment/session_manager.py — DB-backed session state
[ ] src/enrollment/recording_engine.py — full segment capture + validation
[ ] src/enrollment/data_packager.py — ZIP for Colab export
[ ] src/enrollment/ui.py — PyQt6 full-screen enrollment window
[ ] tests/unit/test_sentence_corpus.py — 60 sentences, phoneme coverage
Run: make enroll — full-screen enrollment UI must open.
     Record 3 test sentences — verify saved to data/enrollment/.

═══════════════════════════════════
PHASE 6 — TRAINING (Days 6–7)
═══════════════════════════════════
[ ] src/training/dataset.py — (mel_input, mel_target) PyTorch Dataset
[ ] src/training/dataloader.py — train/val split DataLoader factory
[ ] src/training/optimizer.py — AdamW + cosine LR scheduler
[ ] src/training/callbacks.py — EarlyStopping, ModelCheckpoint
[ ] src/training/metrics.py — MCD + SECS computation
[ ] src/training/checkpoint_manager.py — save/load/rollback safetensors
[ ] src/training/lora_trainer.py — full LoRA training loop
[ ] src/training/idle_scheduler.py — background idle trigger
[ ] src/colab/notebook_generator.py — .ipynb generation
[ ] src/colab/drive_poller.py — Google Drive link polling
[ ] src/colab/colab_launcher.py — open Colab in system browser
[ ] tests/unit/test_lora_trainer.py — loss decreases, checkpoint saves
[ ] tests/unit/test_metrics.py
[ ] tests/unit/test_checkpoint_manager.py
Run: make train-local — training must start with 30+ enrollment segments.
     Verify checkpoint saved to models/lora/.

═══════════════════════════════════
PHASE 7 — PIPELINES (Days 7–8)
═══════════════════════════════════
[ ] src/pipeline/queue_manager.py — asyncio Queue wrappers
[ ] src/pipeline/pipeline_metrics.py — latency tracking per stage
[ ] src/pipeline/outgoing_pipeline.py — full async outgoing pipeline
[ ] src/pipeline/incoming_pipeline.py — full async incoming pipeline
[ ] tests/integration/test_outgoing_pipeline.py
[ ] tests/integration/test_incoming_pipeline.py
Run: benchmark end-to-end latency: python scripts/benchmark_latency.py
     Target: < 750ms average on RTX 3050.

═══════════════════════════════════
PHASE 8 — OVERLAY + TRAY (Days 8–9)
═══════════════════════════════════
[ ] src/overlay/theme.py — colors, fonts, opacity constants
[ ] src/overlay/position_calculator.py — OS-specific position logic
[ ] src/overlay/caption_renderer.py — prefix-stability rendering
[ ] src/overlay/overlay_window.py — PyQt6 always-on-top window
[ ] src/tray/language_selector.py — 8-language radio button submenus
[ ] src/tray/status_monitor.py — GPU temp, latency polling
[ ] src/tray/process_manager.py — subprocess launch/kill/monitor
[ ] src/tray/tray_app.py — pystray menu + orchestration
[ ] src/main.py — entry point + typer CLI commands
[ ] tests/unit/test_caption_renderer.py
[ ] tests/unit/test_position_calculator.py
Run: make run — system tray icon appears.
     Open Zoom/Teams, select "VoiceTranslate Mic" — speak in English, verify Japanese voice output.
     Open YouTube video in any language — verify caption overlay appears above taskbar.

═══════════════════════════════════
PHASE 9 — POLISH + DOCUMENTATION
═══════════════════════════════════
[ ] README.md — complete with: overview, prerequisites, setup steps,
                enrollment guide, training guide, usage guide, troubleshooting
[ ] docs/enrollment_guide.md — step-by-step with screenshots description
[ ] docs/training_guide.md — local vs Colab with exact steps
[ ] docs/audio_routing.md — VB-Audio + BlackHole installation
[ ] docs/languages.md — all 8 languages with NLLB codes
[ ] CHANGELOG.md — 0.1.0 initial release entry
[ ] scripts/benchmark_latency.py — measures all pipeline stages
Run: make test — full test suite must pass with ≥75% coverage.
Run: make lint — zero ruff errors.
Run: make typecheck — zero mypy errors.
```

---

## §12 — GLOBAL ACCEPTANCE CRITERIA

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  GLOBAL ACCEPTANCE CRITERIA                                                  ║
║  The project is ONLY complete when every checkbox below can be ticked.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

STRUCTURAL COMPLETENESS
[ ] Every file in the File Tree (§4) exists on disk
[ ] No files exist that are not in the File Tree
[ ] .env.example documents every environment variable used anywhere in code
[ ] All directories are named exactly as specified
[ ] models/ and data/ directories have .gitkeep files (not committed when populated)

CODE QUALITY
[ ] make lint passes with zero ruff errors
[ ] make typecheck passes with zero mypy errors
[ ] No TODO, FIXME, HACK, or PLACEHOLDER comments remain in production code
[ ] No hard-coded paths, secrets, or API keys
[ ] No print() in production code — loguru logger used everywhere
[ ] All public functions have type signatures and docstrings
[ ] No bare except clauses — all exceptions are specific types

TESTING
[ ] make test passes with ≥75% overall coverage
[ ] All unit tests pass without GPU (mock where necessary)
[ ] Smoke test completes in < 60 seconds
[ ] No tests are order-dependent
[ ] No tests require internet access

FUNCTIONAL ACCEPTANCE CRITERIA
[ ] ENROLLMENT: Full-screen window covers entire laptop display including taskbar area
[ ] ENROLLMENT: Sentence text is large (≥42px), centered, readable on any laptop resolution
[ ] ENROLLMENT: Saying "DONE" ends the current recording segment within 500ms
[ ] ENROLLMENT: 60 complex sentences are available (each ≥15 words)
[ ] ENROLLMENT: WAV files saved correctly to data/enrollment/ with correct naming
[ ] TRAINING LOCAL: LoRA training starts on RTX 3050 after make train-local
[ ] TRAINING LOCAL: Training loss visibly decreases (logged every 50 steps)
[ ] TRAINING LOCAL: Checkpoint saved to models/lora/latest.safetensors
[ ] TRAINING COLAB: Colab notebook generated at colab/train_lora.ipynb
[ ] TRAINING COLAB: Notebook opens in browser automatically
[ ] TRAINING COLAB: After user pastes Drive link, checkpoint downloads automatically
[ ] OUTGOING ASR: Faster-Whisper base transcribes English at < 120ms on GPU
[ ] OUTGOING MT: NLLB translates all 56 language pairs (8×7)
[ ] OUTGOING TTS: CosyVoice2 synthesizes with user's voice (SECS ≥ 0.80 after 1 week)
[ ] OUTGOING END-TO-END: Glass-to-ear latency ≤ 750ms (measured by benchmark script)
[ ] OUTGOING ROUTING: Virtual microphone detected by Zoom, Teams, Google Meet
[ ] INCOMING CAPTION: Caption overlay appears above taskbar on Windows 11
[ ] INCOMING CAPTION: Caption overlay appears above dock on macOS 14
[ ] INCOMING CAPTION: Overlay is click-through (does not block mouse events)
[ ] INCOMING CAPTION: Caption uses prefix-stability (committed text never disappears)
[ ] INCOMING CAPTION: Caption fades after 3 seconds of silence
[ ] INCOMING TTS: Kokoro-82M plays translated audio through speakers (CPU only)
[ ] INCOMING LANGUAGE: Auto-detection fires within first 500ms of speech
[ ] LANGUAGE SUPPORT: All 8 languages work for both outgoing and incoming
[ ] LANGUAGE SUPPORT: Only these 8 languages are supported (no others possible)
[ ] TRAY: System tray icon appears on Windows 11 and macOS 14
[ ] TRAY: Language change takes effect within 2 seconds in running pipelines
[ ] TRAY: GPU temperature displays in real-time (updates every 5s)
[ ] TRAY: Average latency displays in real-time
[ ] TRAY: Quit terminates all processes cleanly (no zombie processes)
[ ] VRAM: Total VRAM used ≤ 3,800 MB on RTX 3050 (4GB card)
[ ] CPU FALLBACK: System switches to CPU fallback when GPU not available
[ ] BACKGROUND TRAINING: Idle scheduler starts training when GPU+CPU both below threshold
[ ] BACKGROUND TRAINING: Training pauses immediately when GPU util rises above threshold
[ ] BACKGROUND TRAINING: LoRA adapter hot-swapped without TTS process restart

DOCUMENTATION
[ ] README.md: overview, prerequisites (Python 3.11, CUDA 12.2, VB-Audio), setup, run, enroll, train
[ ] docs/setup.md: step-by-step with exact commands for Windows 11
[ ] docs/enrollment_guide.md: complete user walkthrough
[ ] docs/training_guide.md: local GPU + Google Colab instructions
[ ] docs/audio_routing.md: VB-Audio Cable install + verification steps
[ ] CHANGELOG.md: 0.1.0 entry with feature list
```

---

## CRITICAL INSTRUCTIONS FOR THE AI AGENT

```
1. READ THIS ENTIRE FILE before writing any code.
2. Follow the Implementation Order (§11) EXACTLY — do not skip phases.
3. After completing each phase, run the specified test command.
4. Fix ALL test failures before proceeding to the next phase.
5. Every file in the File Tree (§4) MUST exist when the project is complete.
6. Do not create files not in the File Tree without documenting why.
7. Do not merge files that are listed separately.
8. Every function must have a type signature and docstring.
9. Use loguru for all logging — never print().
10. All audio device code must be cross-platform (Windows primary, macOS secondary).
11. GPU code must gracefully fall back to CPU when GPU unavailable.
12. The enrollment UI MUST be full-screen — this is not negotiable.
13. The caption overlay MUST appear above the taskbar — test this specifically.
14. Only 8 languages are supported — do not add any others.
15. The project is NOT complete until every acceptance criterion in §12 is met.
16. The Colab notebook must be self-contained — a user who has never seen this
    codebase must be able to open it and train without reading any other file.
17. LoRA training checkpoint must be rollback-safe — quality gates must be enforced.
18. If you are unsure about any requirement, re-read the relevant module spec.
    Do NOT guess. The spec is authoritative.
```