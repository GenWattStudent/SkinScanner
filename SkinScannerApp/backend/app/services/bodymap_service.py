"""
CRUD operations for BodyMapMarker.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy.orm import Session

from app.db.models import BodyMapMarker
from app.core.exceptions import MarkerNotFoundError
from app.schemas.bodymap import (
    BodyMapMarkerCreate,
    BodyMapMarkerList,
    BodyMapMarkerOut,
    BodyMapMarkerUpdate,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _to_schema(marker: BodyMapMarker) -> BodyMapMarkerOut:
    return BodyMapMarkerOut.model_validate(marker)


# ── Public API ───────────────────────────────────────────────────────────────

def list_markers(db: Session, patient_id: int) -> BodyMapMarkerList:
    """Return all markers for a given patient."""
    items = (
        db.query(BodyMapMarker)
        .filter(BodyMapMarker.patient_id == patient_id)
        .order_by(BodyMapMarker.created_at.desc())
        .all()
    )
    return BodyMapMarkerList(total=len(items), items=[_to_schema(m) for m in items])


def get_marker(db: Session, marker_id: int) -> BodyMapMarker:
    """Fetch a single marker or raise."""
    marker = db.query(BodyMapMarker).filter(BodyMapMarker.id == marker_id).first()
    if marker is None:
        raise MarkerNotFoundError(marker_id)
    return marker


def create_marker(db: Session, payload: BodyMapMarkerCreate) -> BodyMapMarkerOut:
    """Insert a new marker row."""
    marker = BodyMapMarker(**payload.model_dump())
    db.add(marker)
    db.commit()
    db.refresh(marker)
    logger.info(f"Created body-map marker id={marker.id} view={marker.view}")
    return _to_schema(marker)


def update_marker(
    db: Session, marker_id: int, payload: BodyMapMarkerUpdate
) -> BodyMapMarkerOut:
    """Partially update an existing marker."""
    marker = get_marker(db, marker_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(marker, field, value)
    db.commit()
    db.refresh(marker)
    logger.info(f"Updated body-map marker id={marker.id}")
    return _to_schema(marker)


def delete_marker(db: Session, marker_id: int) -> None:
    """Delete a marker by ID."""
    marker = get_marker(db, marker_id)
    db.delete(marker)
    db.commit()
    logger.info(f"Deleted body-map marker id={marker_id}")
