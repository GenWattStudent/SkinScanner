"""Pydantic schemas for the Patient feature."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Payload to create a new patient."""

    name: str = Field(min_length=1, max_length=200, description="Patient name")
    notes: str | None = Field(default=None, description="Optional notes about the patient")


class PatientUpdate(BaseModel):
    """Payload to update an existing patient (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None


class PatientOut(BaseModel):
    """Response schema for a single patient."""

    id: int
    created_at: datetime
    updated_at: datetime
    name: str
    notes: str | None
    marker_count: int = 0

    model_config = {"from_attributes": True}


class PatientList(BaseModel):
    """List of all patients."""

    total: int
    items: list[PatientOut]
