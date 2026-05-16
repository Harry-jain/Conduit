# Enrollment Guide

## Goal

Collect clean speech segments and mel targets for voice adaptation training.

## Steps

1. Run enrollment:
   - `python -m src.main enroll`
2. Read each sentence clearly.
3. Keep a constant mic distance and avoid background noise.
4. Complete all 60 sentences.

## Saved artifacts

1. Audio:
   - `data/enrollment/segment_001.wav` ... `segment_060.wav`
2. Mel spectrograms:
   - `data/enrollment/segment_001_mel.npy` ... `segment_060_mel.npy`
3. Metadata:
   - `data/enrollment/metadata.json`

## Quality expectations

1. Duration per segment: 3-30 seconds
2. SNR target: >= 15 dB
3. Minimal clipping
