from __future__ import annotations

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class HealthCheck(BaseModel):
    status: str
    models_loaded: list[str]
    device: str
    gpu_name: str | None = None
    gpu_memory_gb: float | None = None


class ModelInfo(BaseModel):
    model_type: str
    label: str
    available: bool
