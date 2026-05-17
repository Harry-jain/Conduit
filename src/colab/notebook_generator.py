"""Generate self-contained Colab notebook."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import nbformat as nbf


@dataclass
class ColabNotebookGenerator:
    """Programmatic notebook generator."""

    config: object

    def generate(self, output_path: str, training_data_zip: str) -> str:
        """Generate notebook with required cells."""
        nb = nbf.v4.new_notebook()
        zip_name = Path(training_data_zip).name
        cells = [
            (
                "import torch\n"
                "print('GPU:', torch.cuda.is_available(), "
                "torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
            ),
            "pip install torch==2.3.1 peft==0.12.0 transformers==4.43.3 torchaudio==2.3.1",
            "from google.colab import drive\ndrive.mount('/content/drive')",
            (
                "from google.colab import files\n"
                "uploaded = files.upload()\n"
                f"if '{zip_name}' not in uploaded:\n"
                "    print('Uploaded files:', list(uploaded.keys()))"
            ),
            (
                "import zipfile, os\n"
                "os.makedirs('/content/training_data', exist_ok=True)\n"
                "zipfile.ZipFile(list(uploaded.keys())[0]).extractall('/content/training_data')"
            ),
            (
                "import glob, numpy as np\n"
                "import torch, torch.nn as nn\n"
                "from torch.utils.data import Dataset, DataLoader\n"
                "from peft import LoraConfig, get_peft_model\n"
                "class MelDataset(Dataset):\n"
                "    def __init__(self, root='/content/training_data'):\n"
                "        self.files = sorted(glob.glob(root + '/**/*_mel.npy', recursive=True))\n"
                "    def __len__(self):\n"
                "        return len(self.files)\n"
                "    def __getitem__(self, idx):\n"
                "        mel = np.load(self.files[idx]).astype(np.float32)\n"
                "        mel = torch.from_numpy(mel).transpose(0, 1)\n"
                "        return mel, mel\n"
                "base = nn.Sequential(nn.Linear(80,80), nn.ReLU(), nn.Linear(80,80)).cuda() if torch.cuda.is_available() else nn.Sequential(nn.Linear(80,80), nn.ReLU(), nn.Linear(80,80))\n"
                "cfg = LoraConfig(r=8, lora_alpha=16, target_modules=['0','2'])\n"
                "model = get_peft_model(base, cfg)"
            ),
            (
                "dataset = MelDataset()\n"
                "loader = DataLoader(dataset, batch_size=4, shuffle=True)\n"
                "optim = torch.optim.AdamW(model.parameters(), lr=1e-4)\n"
                "loss_fn = nn.L1Loss()\n"
                "device = 'cuda' if torch.cuda.is_available() else 'cpu'\n"
                "model.to(device)\n"
                "for epoch in range(20):\n"
                "    epoch_loss = 0.0\n"
                "    for x, y in loader:\n"
                "        x = x.to(device)\n"
                "        y = y.to(device)\n"
                "        pred = model(x)\n"
                "        loss = loss_fn(pred, y)\n"
                "        optim.zero_grad()\n"
                "        loss.backward()\n"
                "        optim.step()\n"
                "        epoch_loss += float(loss.item())\n"
                "    print(f'Epoch {epoch+1}/20 loss={epoch_loss/max(len(loader),1):.4f}')"
            ),
            (
                "from datetime import datetime\n"
                "import os\n"
                "os.makedirs('/content/drive/MyDrive/voicetranslate', exist_ok=True)\n"
                "path=f'/content/drive/MyDrive/voicetranslate/"
                'lora_checkpoint_{datetime.now().strftime("%Y%m%d_%H%M%S")}.safetensors\'\n'
                "torch.save(model.state_dict(), path)\n"
                "print('Saved to', path)"
            ),
            (
                "import urllib.parse\n"
                "shareable = 'https://drive.google.com/drive/my-drive'\n"
                "print('Share this path from Drive UI:', shareable)\n"
                "print('Checkpoint filename:', path.split('/')[-1])"
            ),
        ]
        nb.cells = [nbf.v4.new_code_cell(c) for c in cells]
        nbf.validate(nb)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(nbf.writes(nb), encoding="utf-8")
        return str(out)
