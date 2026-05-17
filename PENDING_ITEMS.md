# Pending Items (Cross-Referenced to `antigravity.md`)

This file tracks what is **still pending** against `D:\Conduit-root\.antigravity\antigravity.md`.

## Implemented in this continuation

- Unit-test execution is unblocked in minimal environments (explicit fallbacks for missing optional ML/audio libs):
  - `src/core/config.py`
  - `src/signal/stft.py`
  - `src/signal/mfcc.py`
  - `src/signal/f0.py`
  - `src/audio/denoiser.py`
  - `src/audio/vad.py`
- Enrollment corpus corrected to exactly 60 sentences:
  - `src/enrollment/sentence_corpus.py`
- Current status: `tests/unit` passes (`16 passed`).
- New end-user workflow components:
  - Control panel command with mic/speaker selectors and start/stop service controls (`python -m src.main control-panel`)
  - Tray actions to start/stop outgoing and incoming services plus training/enrollment shortcuts
  - Process monitor with automatic service restart support
  - Extended enrollment persistence metadata and configurable audio save format (`wav` / `flac`)
  - End-to-end usage guide for local + Colab training and browser/app routing:
    - `docs/from_scratch_workflow.md`

## Still Pending

| ID | Status | Pending item | Spec cross-reference | Current code area | What is missing |
|---|---|---|---|---|---|
| P-01 | **Partial** | Real model-backed ASR/MT/TTS inference | §2 (model stack), §5 modules `models/asr/*`, `models/mt/*`, `models/tts/*`, §12 functional checks | `src/models/asr`, `src/models/mt`, `src/models/tts` | Added optional real backend hooks for Faster-Whisper and HF NLLB; still pending fully production implementations for CosyVoice/Kokoro and strict benchmark acceptance behavior. |
| P-02 | **Partial** | Production-grade cross-platform audio backends | §5 modules `audio/*`, `platform/windows/*`, `platform/macos/*`, §12 audio routing checks | `src/audio/*`, `src/platform/*` | Implemented live taskbar/dock metric queries and active capture/write backends; remaining work is hardware-validated latency tuning and app-level device QA on target machines. |
| P-03 | **Partial** | Full PyQt enrollment UX contract | §5 `enrollment/ui.py`, §12 enrollment criteria | `src/enrollment/ui.py` | UI now captures real microphone audio, updates waveform from live chunks, and ends segments on VAD/DONE spotting; remaining work is stronger streaming word-level recognition confidence handling. |
| P-04 | **Pending** | Training pipeline quality-gated LoRA workflow | §5 `training/*`, §6 `training_runs`, §12 training criteria | `src/training/*` | DB tracking added for training runs, but full production LoRA quality gates (MCD/SECS rollback semantics and model-specific adapter training) remain incomplete. |
| P-05 | **Pending** | End-to-end async pipeline robustness and latency targets | §5 `pipeline/*`, §12 latency and resilience criteria | `src/pipeline/*` | Pipelines run and now persist metrics to DB; full stage-level robustness and guaranteed <750ms measured target are still pending. |
| P-06 | **Partial** | OS-native overlay behavior parity | §5 `overlay/overlay_window.py`, §12 incoming caption criteria | `src/overlay/*`, `src/platform/windows/overlay_win.py`, `src/platform/macos/overlay_mac.py` | Overlay now positions using real screen reserve/taskbar/dock values and includes hold/fade timing + CJK font fallback; remaining native edge cases need hardware validation on multi-monitor setups. |
| P-07 | **Mostly done** | Tray orchestration and self-healing process manager | §5 `tray/*`, §12 tray criteria | `src/tray/*` | Added 8-language radio menus (source/target/display), tts voice selector, 5s status monitor polling, restart monitor, and settings action; remaining is long-run reliability validation on both OSes. |
| P-08 | **Partial** | Database-backed runtime state integration | §3 inter-process coordination, §6 schema usage | `src/core/database.py`, services | Implemented user config upsert/read, enrollment/training session persistence, and pipeline metrics inserts. Remaining: broader service-level config sync and richer runtime state coverage. |
| P-09 | **Partial** | Colab workflow completeness | §5 `colab/notebook_generator.py`, §12 Colab criteria | `src/colab/*`, `colab/train_lora.ipynb` | Notebook cells now include a real train loop scaffold and checkpoint save; drive poller now validates and extracts checkpoints. Remaining: user auth/Drive permission edge-case handling in live Colab runs. |
| P-10 | **Mostly done** | Documentation completeness and exactness | §9 docs/tests expectations, §12 documentation criteria | `README.md`, `docs/*.md` | Added expanded setup/training/enrollment/audio and from-scratch workflow docs. Remaining: final troubleshooting matrix and full production examples for each OS path. |
| P-11 | **Partial** | Full quality gates: lint/typecheck/full test matrix | §10 commands, §12 code quality and testing criteria | repo-wide | Unit + integration + lint + mypy now pass in this environment. Remaining: full coverage target validation and hardware-dependent acceptance tests. |

## Dependency Cross-Reference (execution order)

1. **P-02 + P-01** (real audio + real models) unblock accurate pipelines.
2. **P-05** depends on P-01/P-02 and enables realistic latency/robustness.
3. **P-03 + P-04 + P-09** depend on stable audio/model/training foundations.
4. **P-06 + P-07 + P-08** complete platform/runtime orchestration.
5. **P-10 + P-11** finalize release acceptance.
