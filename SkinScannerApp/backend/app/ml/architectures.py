"""
Custom CNN architecture — identical to the original src/custom_arch.py
but without Streamlit / Pandas imports.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class CustomCNN(nn.Module):
    """Lightweight baseline CNN (3 conv blocks → FC head)."""

    def __init__(self, num_classes: int, img_size: int = 224) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        # After 3× MaxPool(2,2): spatial dim = img_size // 8
        flat_dim = 128 * (img_size // 8) * (img_size // 8)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(flat_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)
