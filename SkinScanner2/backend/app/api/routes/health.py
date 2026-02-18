from __future__ import annotations

import torch
from fastapi import APIRouter, Request

from app.core.config import DEVICE
from app.ml.constants import MODEL_FILES
from app.schemas.common import HealthCheck, ModelInfo

router = APIRouter(tags=["Health"])

_MODEL_LABELS: dict[str, str] = {
    "mobilenet": "MobileNetV3 Large",
    "resnet50": "ResNet-50",
    "customcnn": "Custom CNN (Baseline)",
    "vit": "Vision Transformer B/16",
}


@router.get(
    "/health",
    response_model=HealthCheck,
    summary="API health check",
)
async def health(request: Request) -> HealthCheck:
    gpu_name: str | None = None
    gpu_memory_gb: float | None = None

    if DEVICE.type == "cuda":
        gpu_name = torch.cuda.get_device_name(DEVICE)
        props = torch.cuda.get_device_properties(DEVICE)
        gpu_memory_gb = round(props.total_memory / (1024 ** 3), 1)

    return HealthCheck(
        status="ok",
        models_loaded=list(request.app.state.models.keys()),
        device=str(DEVICE),
        gpu_name=gpu_name,
        gpu_memory_gb=gpu_memory_gb,
    )


@router.get(
    "/models",
    response_model=list[ModelInfo],
    summary="List all models and their availability",
)
async def list_models(request: Request) -> list[ModelInfo]:
    loaded: set[str] = set(request.app.state.models.keys())
    return [
        ModelInfo(
            model_type=mt,
            label=_MODEL_LABELS.get(mt, mt),
            available=mt in loaded,
        )
        for mt in MODEL_FILES
    ]
