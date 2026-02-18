"""
Image pre-processing, prediction, and Grad-CAM heatmap generation.
Identical logic to src/processing.py — Streamlit dependency removed.
"""
from __future__ import annotations

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from torchvision import transforms
from loguru import logger

from app.core.config import DEVICE, settings
from app.ml.constants import CLASSES


# ── ViT reshape helper ───────────────────────────────────────────────────────

def _reshape_transform_vit(
    tensor: torch.Tensor, height: int = 14, width: int = 14
) -> torch.Tensor:
    """Remove CLS token and reshape patch tokens → spatial feature map."""
    result = tensor[:, 1:, :].reshape(
        tensor.size(0), height, width, tensor.size(2)
    )
    return result.transpose(2, 3).transpose(1, 2)


# ── Processor ───────────────────────────────────────────────────────────────

class ImageProcessor:
    """Handles image transforms, top-k prediction, and Grad-CAM generation."""

    def __init__(self) -> None:
        self.device = DEVICE
        self.transform = transforms.Compose(
            [
                transforms.Resize((settings.img_size, settings.img_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    # ── Preprocessing ────────────────────────────────────────────────────────

    def prepare(self, image: Image.Image) -> torch.Tensor:
        """PIL Image → normalised tensor (1, C, H, W) on device."""
        return self.transform(image).unsqueeze(0).to(self.device)

    # ── Inference ────────────────────────────────────────────────────────────

    def predict(
        self, model: nn.Module, tensor: torch.Tensor, top_k: int = 3
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return (probabilities, class_indices) for top-k classes."""
        with torch.no_grad():
            output = model(tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            top_probs, top_idx = torch.topk(probs, top_k)
        return top_probs.cpu().numpy()[0], top_idx.cpu().numpy()[0]

    # ── Grad-CAM ─────────────────────────────────────────────────────────────

    def generate_heatmap(
        self,
        model: nn.Module,
        tensor: torch.Tensor,
        original_image: Image.Image,
        model_type: str,
    ) -> np.ndarray:
        """
        Return an RGB numpy array (H×W×3, uint8) with Grad-CAM overlay.
        Falls back to a plain resized image on any error.
        """
        fallback = cv2.resize(
            np.array(original_image),
            (settings.img_size, settings.img_size),
        )

        try:
            target_layers = None
            reshape_transform = None

            if model_type == "resnet50":
                target_layers = [model.layer4[-1]]

            elif model_type == "mobilenet":
                target_layers = [model.features[-1]]

            elif model_type == "vit":
                target_layers = [model.encoder.layers[-1].ln_1]
                reshape_transform = _reshape_transform_vit

            elif model_type == "customcnn":
                # Prefer model.features; fall back to last Conv2d in module tree
                if hasattr(model, "features"):
                    for layer in reversed(list(model.features)):
                        if isinstance(layer, nn.Conv2d):
                            target_layers = [layer]
                            break
                if target_layers is None:
                    conv_layers = [
                        m for m in model.modules() if isinstance(m, nn.Conv2d)
                    ]
                    if conv_layers:
                        target_layers = [conv_layers[-1]]

            if target_layers is None:
                logger.warning(f"No Grad-CAM target layer found for model_type='{model_type}'")
                return fallback

            cam = GradCAM(
                model=model,
                target_layers=target_layers,
                reshape_transform=reshape_transform,
            )
            grayscale_cam = cam(input_tensor=tensor, targets=None)[0]

            rgb_img = cv2.resize(
                np.float32(original_image) / 255.0,
                (settings.img_size, settings.img_size),
            )
            return show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

        except Exception as exc:
            logger.warning(f"Grad-CAM failed for model_type='{model_type}': {exc}")
            return fallback
