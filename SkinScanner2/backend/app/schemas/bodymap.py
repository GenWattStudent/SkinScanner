"""Pydantic schemas for the Body Map feature."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BodyMapMarkerCreate(BaseModel):
    """Payload to create a new body-map marker."""

    x: float = Field(ge=0.0, le=1.0, description="Normalised X position on the SVG (0–1)")
    y: float = Field(ge=0.0, le=1.0, description="Normalised Y position on the SVG (0–1)")
    view: str = Field(default="front", pattern="^(front|back)$", description="Body view: 'front' or 'back'")
    label: str = Field(default="", max_length=200, description="Short label for the marker")
    notes: str | None = Field(default=None, description="Optional longer notes")
    scan_id: int | None = Field(default=None, description="Optional linked scan result ID")
    patient_id: int = Field(description="Owning patient ID")


class BodyMapMarkerUpdate(BaseModel):
    """Payload to update an existing marker (all fields optional)."""

    x: float | None = Field(default=None, ge=0.0, le=1.0)
    y: float | None = Field(default=None, ge=0.0, le=1.0)
    view: str | None = Field(default=None, pattern="^(front|back)$")
    label: str | None = Field(default=None, max_length=200)
    notes: str | None = None
    scan_id: int | None = None


class BodyMapMarkerOut(BaseModel):
    """Response schema for a single marker."""

    id: int
    created_at: datetime
    updated_at: datetime
    x: float
    y: float
    view: str
    label: str
    notes: str | None
    scan_id: int | None
    patient_id: int

    model_config = {"from_attributes": True}


class BodyMapMarkerList(BaseModel):
    """Paginated list of markers."""

    total: int
    items: list[BodyMapMarkerOut]
