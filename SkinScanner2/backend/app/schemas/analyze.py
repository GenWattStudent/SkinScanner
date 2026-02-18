from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ClassPrediction(BaseModel):
    """A single class prediction with confidence and metadata."""

    class_key: str = Field(description="Internal class identifier, e.g. 'Melanoma'")
    class_pl: str = Field(description="Polish display name")
    class_en: str = Field(description="English display name")
    confidence: float = Field(ge=0.0, le=1.0, description="Softmax probability 0–1")
    risk_level: int = Field(ge=0, le=2, description="0=benign, 1=watch, 2=see doctor")
    description_pl: str
    description_en: str


class ModelResult(BaseModel):
    """Result from a single model."""

    model_type: str = Field(description="e.g. mobilenet, resnet50, customcnn, vit")
    model_label: str = Field(description="Human-readable label, e.g. 'MobileNetV3'")

    # Top-1 result for this model
    primary_prediction: ClassPrediction

    # Top-3 results (index 0 == primary)
    top_predictions: list[ClassPrediction]

    # Grad-CAM heatmap for this model (data:image/png;base64,…)
    heatmap_base64: str


class AnalyzeResponse(BaseModel):
    """Full response payload — one image analysed by ALL loaded models."""

    scan_id: int = Field(description="Auto-generated database ID for this scan")
    timestamp: datetime

    # Per-model results (one entry per loaded model)
    model_results: list[ModelResult]

    # Consensus: aggregated top-1 prediction across all models
    consensus_class_key: str
    consensus_risk_level: int = Field(ge=0, le=2)
    consensus_confidence: float = Field(ge=0.0, le=1.0)

    # Original image (shared across all models)
    original_image_base64: str
