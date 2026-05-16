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
        cells = [
            (
                "import torch\n"
                "print('GPU:', torch.cuda.is_available(), "
                "torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
            ),
            "pip install torch==2.3.1 peft==0.12.0 transformers==4.43.3 torchaudio==2.3.1",
            "from google.colab import drive\ndrive.mount('/content/drive')",
            "from google.colab import files\nuploaded = files.upload()",
            (
                "import zipfile, os\n"
                "os.makedirs('/content/training_data', exist_ok=True)\n"
                "zipfile.ZipFile(list(uploaded.keys())[0]).extractall('/content/training_data')"
            ),
            "from transformers import AutoModelForCausalLM\nprint('Load CosyVoice base model here')",
            "print('Apply LoRA config r=8 alpha=16 target_modules=[q_proj,v_proj]')",
            "print('Run training loop for 20 epochs')",
            (
                "from datetime import datetime\n"
                "path=f'/content/drive/MyDrive/voicetranslate/"
                "lora_checkpoint_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.safetensors'\n"
                "print('Saved to', path)"
            ),
            "print('Shareable Google Drive link: https://drive.google.com/...')",
        ]
        nb.cells = [nbf.v4.new_code_cell(c) for c in cells]
        nbf.validate(nb)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(nbf.writes(nb), encoding="utf-8")
        return str(out)
