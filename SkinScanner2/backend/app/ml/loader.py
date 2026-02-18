"""
Loads PyTorch model weights from .pth files at application startup.
No Streamlit caching — models are stored in app.state.models instead.
"""
from __future__ import annotations

from collections import OrderedDict

import torch
import torch.nn as nn
from loguru import logger
from torchvision import models as tv_models

from app.core.config import DEVICE, settings
from app.ml.architectures import CustomCNN
from app.ml.constants import CLASSES, MODEL_FILES


class ModelLoader:
    """Builds model architectures and loads pre-trained weights."""

    def __init__(self) -> None:
        self.device = DEVICE
        self.models_dir = settings.models_dir
        self._num_classes = len(CLASSES)

    # ── Architecture factory ─────────────────────────────────────────────────

    def _build(self, model_type: str) -> nn.Module:
        n = self._num_classes
        if model_type == "resnet50":
            m = tv_models.resnet50(weights=None)
            m.fc = nn.Linear(m.fc.in_features, n)

        elif model_type == "mobilenet":
            m = tv_models.mobilenet_v3_large(weights=None)
            m.classifier[3] = nn.Linear(m.classifier[3].in_features, n)

        elif model_type == "customcnn":
            m = CustomCNN(num_classes=n, img_size=settings.img_size)

        elif model_type == "vit":
            m = tv_models.vit_b_16(weights=None)
            m.heads.head = nn.Linear(m.heads.head.in_features, n)

        else:
            raise ValueError(f"Unknown model_type: '{model_type}'")

        return m

    # ── Single model loading ─────────────────────────────────────────────────

    def load(self, model_type: str) -> nn.Module | None:
        filename = MODEL_FILES.get(model_type)
        if not filename:
            logger.warning(f"No .pth mapping for model_type='{model_type}'")
            return None

        model_path = self.models_dir / filename
        if not model_path.exists():
            logger.warning(f"Weight file not found: {model_path}")
            return None

        try:
            model = self._build(model_type)

            # Load weights — strip DataParallel 'module.' prefix if present
            raw_sd = torch.load(model_path, map_location="cpu")
            clean_sd = OrderedDict(
                (k[7:] if k.startswith("module.") else k, v)
                for k, v in raw_sd.items()
            )
            model.load_state_dict(clean_sd)
            model.to(self.device)
            model.eval()

            logger.info(f"✓ Loaded [{model_type}] from {model_path.name}")
            return model

        except Exception as exc:
            logger.error(f"✗ Failed to load [{model_type}]: {exc}")
            return None

    # ── Bulk load at startup ─────────────────────────────────────────────────

    def load_all(self) -> dict[str, nn.Module]:
        models: dict[str, nn.Module] = {}
        for model_type in MODEL_FILES:
            m = self.load(model_type)
            if m is not None:
                models[model_type] = m

        logger.info(
            f"Models ready: {list(models.keys())} "
            f"({len(models)}/{len(MODEL_FILES)}) | device={self.device}"
        )
        return models
