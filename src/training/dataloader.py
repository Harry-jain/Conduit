"""Dataloader factory."""

from __future__ import annotations

from torch.utils.data import DataLoader, random_split

from src.training.dataset import MelPairDataset


def build_dataloaders(
    data_dir: str = "data/training", batch_size: int = 4
) -> tuple[DataLoader, DataLoader]:
    """Build train and validation dataloaders."""
    ds = MelPairDataset(data_dir=data_dir)
    if len(ds) == 0:
        return DataLoader(ds, batch_size=batch_size), DataLoader(ds, batch_size=batch_size)
    val_size = max(int(len(ds) * 0.2), 1)
    train_size = len(ds) - val_size
    train_ds, val_ds = random_split(ds, [train_size, val_size])
    return DataLoader(train_ds, batch_size=batch_size, shuffle=True), DataLoader(
        val_ds, batch_size=batch_size
    )
