"""Training data ZIP packager."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def package_training_data(
    source_dir: str = "data/enrollment", output_zip: str = "data/exports/training_data.zip"
) -> str:
    """Package enrollment data as zip for Colab upload."""
    src = Path(source_dir)
    out = Path(output_zip)
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_DEFLATED) as zf:
        for path in src.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(src))
    return str(out)
