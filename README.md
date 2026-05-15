# Conduit

Conduit is a real-time desktop speech translation and captioning application designed to help people communicate across languages during live meetings, calls, interviews, and collaborative sessions.

## Quick Start
1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies with `pip install -e ".[dev]"`.
3. Copy `.env.example` to `.env`.
4. Run `make run`.

See `docs/setup.md` for full setup.

---

# Project Goals

Conduit is being built to solve a simple but difficult problem: real-time multilingual communication without forcing users to manually copy text, switch apps, or rely on slow post-processing tools.

Core goals:

- Translate speech in real time with minimal delay
- Provide live captions for both incoming and outgoing speech
- Support a background desktop workflow
- Offer modular architecture for cloud and local execution
- Prioritize privacy, consent, and audio control
- Scale from MVP to production-grade deployment

---

# What Conduit Will Do

At a high level, Conduit will:

1. Capture microphone input from the user
2. Capture incoming meeting audio through system loopback
3. Detect speech segments using Voice Activity Detection (VAD)
4. Convert speech into text using ASR models
5. Translate the text into the target language
6. Render stable live captions
7. Generate translated speech using TTS
8. Route translated speech back into the meeting
9. Provide language, device, and routing controls
10. Gracefully degrade under hardware pressure

The application is intended to support two complementary experiences:

- Caption-first mode
- Voice translation mode

---

# Planned Architecture

Conduit follows a cascaded pipeline architecture:

Audio Capture → VAD → ASR → Translation → TTS → Audio Output / Captions

This design keeps each stage modular and independently optimizable.

## Why Cascaded Architecture?

A cascaded pipeline allows:

- Easier debugging
- Better model replacement flexibility
- Intermediate caption generation
- Independent optimization of ASR, MT, and TTS
- Flexible deployment across cloud and local hardware

The MVP will likely rely on cloud APIs initially before transitioning toward local inference.

---

# Development Strategy

## Phase 1 — Prototype

Goal:
Validate the end-to-end pipeline.

Objectives:

- Reliable audio capture
- Streaming ASR
- Real-time translation
- Caption rendering
- TTS playback
- Latency benchmarking

Cloud APIs will be prioritized during this stage for faster iteration.

---

## Phase 2 — Desktop Integration

Goal:
Build a seamless desktop experience.

Objectives:

- System tray integration
- Audio device management
- Virtual microphone routing
- Caption stabilization
- Improved onboarding flow
- Cross-platform desktop shell

---

## Phase 3 — Local Inference

Goal:
Reduce cloud dependency.

Objectives:

- Local ASR integration
- Local translation models
- Local TTS inference
- Hardware-aware optimization
- CPU / iGPU acceleration
- Offline-capable workflows

---

## Phase 4 — Production Hardening

Goal:
Make the system reliable for real-world use.

Objectives:

- Stability optimization
- Failure recovery
- Diagnostics and logging
- Consent and compliance systems
- Packaging and installers
- Release-ready builds

---

# Expected Technology Stack

## Frontend

- Electron or Tauri
- React-based UI
- System tray integration
- Real-time caption renderer

## Backend

- Python or Rust
- WebSocket streaming
- Background processing workers
- Local inference orchestration

## Audio Layer

- WASAPI / CoreAudio
- System loopback capture
- Virtual microphone routing
- Noise suppression
- Echo mitigation

## AI / ML Layer

- Speech Recognition (ASR)
- Machine Translation (MT)
- Text-to-Speech (TTS)
- Voice Activity Detection (VAD)
- Optional diarization

---

# Potential Model Stack

## ASR

- Faster-Whisper
- Whisper Tiny INT8
- Whisper v3 Turbo
- Deepgram Nova

## Translation

- NLLB
- Opus-MT
- GPT-based translation APIs
- LLaMA-based translation pipelines

## TTS

- Kokoro-82M
- XTTS
- Fish Speech
- Cartesia Sonic

---

# Resources Needed

## Human Resources

The project benefits from:

- Frontend developer
- Backend engineer
- ML engineer
- Systems/audio engineer
- UX designer
- QA/testing support

---

## Hardware Resources

Recommended testing hardware:

- CPU-only laptop
- Integrated GPU laptop
- NVIDIA GPU system
- macOS device
- Multiple microphones/headphones

---

## Software Resources

Needed tooling includes:

- Audio routing APIs
- Virtual audio devices
- AI inference frameworks
- Packaging tools
- Benchmark tooling
- Logging systems

---

# Key Technical Challenges

## 1. Latency

The system must remain conversational. High latency destroys usability.

## 2. Audio Routing

Cross-platform audio routing is difficult and fragile.

## 3. Caption Stability

Streaming captions tend to flicker and rewrite themselves.

## 4. Hardware Constraints

Running ASR + MT + TTS simultaneously is resource intensive.

## 5. Privacy and Consent

Live speech systems require strong transparency and user control.

## 6. Cross-Platform Compatibility

Windows and macOS audio systems behave very differently.

---

# Success Criteria

Conduit is considered successful when it can:

- Process speech reliably in real time
- Maintain usable latency
- Produce stable captions
- Run on consumer hardware
- Minimize setup complexity
- Scale from MVP to production

---

# Preliminary Roadmap

- Week 1–2 → Audio capture proof of concept
- Week 3–4 → ASR + Translation pipeline
- Week 5–6 → Captions and UI
- Week 7–8 → TTS + virtual audio output
- Week 9–10 → Optimization and benchmarking
- Week 11–12 → Local inference integration
- Week 13+ → Packaging and release preparation

---

# Future Enhancements

Potential future features:

- Speaker diarization
- Voice cloning
- Meeting summaries
- Domain-specific glossaries
- Automatic language detection
- Offline-first deployment
- Enterprise compliance controls

---

# Repository Status

Current status:
Early-stage architecture and planning.

Planned additions:

- Source code
- Architecture diagrams
- Benchmarks
- Installation instructions
- Model evaluations
- Troubleshooting guides

---

# Contribution Notes

Contributions are welcome in:

- Audio systems
- Real-time streaming
- ML optimization
- Desktop UX
- Accessibility
- Performance engineering

---

# License

To be decided.

---

# Notes

This README currently serves as an architectural placeholder and project overview while development is still in early planning and prototyping stages.

