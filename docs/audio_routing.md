# Audio Routing

## Windows

1. Install VB-Audio Virtual Cable.
2. Set Conduit env:
   - `VOICETRANSLATE_VIRTUAL_MIC_DEVICE=CABLE Input`
   - `VOICETRANSLATE_LOOPBACK_DEVICE=CABLE Output` or speaker loopback source
3. In conferencing app (Zoom/Teams/Meet):
   - Microphone: `CABLE Input`
4. Start Conduit outgoing pipeline:
   - `python -m src.main run-outgoing`

## macOS

1. Install BlackHole 2ch.
2. Set Conduit env:
   - `VOICETRANSLATE_VIRTUAL_MIC_DEVICE=BlackHole 2ch`
   - `VOICETRANSLATE_LOOPBACK_DEVICE=BlackHole 2ch`
3. In conferencing app:
   - Microphone: `BlackHole 2ch`
4. Start Conduit outgoing pipeline:
   - `python -m src.main run-outgoing`

## Verification

1. Open conferencing app audio settings.
2. Speak and verify app microphone level meter responds to Conduit output.
