"""Optimizer and scheduler factory."""

from __future__ import annotations

import torch


def build_optimizer_and_scheduler(
    model: torch.nn.Module, lr: float = 1e-4
) -> tuple[torch.optim.Optimizer, object]:
    """Build AdamW optimizer with cosine schedule."""
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4, betas=(0.9, 0.999))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=200, eta_min=1e-6)
    return optimizer, scheduler
