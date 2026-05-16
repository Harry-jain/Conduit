# Training Guide

## Local training (GPU or CPU fallback)

1. Ensure enrollment/training data is present in:
   - `data/enrollment`
   - `data/training`
2. Start local training:
   - `python -m src.main train --mode local`
3. Checkpoints are written to:
   - `models/lora/checkpoint_<epoch>_<step>.safetensors`
   - `models/lora/latest.safetensors`

## Colab training

1. Generate notebook:
   - `python -m src.main train --mode colab`
2. Open and run:
   - `colab/train_lora.ipynb`
3. Use GPU runtime in Colab.
4. Upload training data ZIP when prompted.
5. Download resulting checkpoint and place/update:
   - `models/lora/latest.safetensors`

## Runtime requirements

1. Local:
   - Python 3.11
   - Torch 2.3.1
   - GPU optional; CPU fallback supported
2. Colab:
   - Python 3 kernel
   - GPU runtime (T4/A100 recommended)
