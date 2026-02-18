from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ModelResultEntry(BaseModel):
    """Per-model result inside a history entry."""

    model_type: str
    model_label: str
    class_key: str
    class_pl: str
    class_en: str
    confidence: float
    risk_level: int
    # top-3 serialised from DB
    top3: list[dict] | None = None
    # URL to fetch heatmap image
    image_heatmap_url: str | None = None


class HistoryEntry(BaseModel):
    """One scan entry as returned by the history API."""

    id: int
    timestamp: datetime

    # Consensus (aggregated across all models)
    consensus_class_key: str
    consensus_risk_level: int
    consensus_confidence: float

    # Per-model breakdown
    model_results: list[ModelResultEntry]

    # Caller-facing URL for original image
    image_original_url: str | None = None


class HistoryList(BaseModel):
    total: int
    page: int
    limit: int
    items: list[HistoryEntry]
