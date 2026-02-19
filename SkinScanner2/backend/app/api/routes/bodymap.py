"""
REST routes for the Body Map feature.

Endpoints
─────────
GET    /bodymap/markers        → list all markers
POST   /bodymap/markers        → create a marker
GET    /bodymap/markers/{id}   → get a single marker
PATCH  /bodymap/markers/{id}   → update a marker
DELETE /bodymap/markers/{id}   → delete a marker
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_db
from app.schemas.bodymap import (
    BodyMapMarkerCreate,
    BodyMapMarkerList,
    BodyMapMarkerOut,
    BodyMapMarkerUpdate,
)
from app.services import bodymap_service

router = APIRouter(prefix="/bodymap", tags=["Body Map"])


@router.get(
    "/markers",
    response_model=BodyMapMarkerList,
    summary="List body-map markers for a patient",
)
def list_markers(
    patient_id: int = Query(..., description="Patient ID to filter markers"),
    db=Depends(get_db),
) -> BodyMapMarkerList:
    return bodymap_service.list_markers(db, patient_id)


@router.post(
    "/markers",
    response_model=BodyMapMarkerOut,
    status_code=201,
    summary="Create a body-map marker",
)
def create_marker(payload: BodyMapMarkerCreate, db=Depends(get_db)) -> BodyMapMarkerOut:
    return bodymap_service.create_marker(db, payload)


@router.get(
    "/markers/{marker_id}",
    response_model=BodyMapMarkerOut,
    summary="Get a single body-map marker",
)
def get_marker(marker_id: int, db=Depends(get_db)) -> BodyMapMarkerOut:
    marker = bodymap_service.get_marker(db, marker_id)
    return bodymap_service._to_schema(marker)


@router.patch(
    "/markers/{marker_id}",
    response_model=BodyMapMarkerOut,
    summary="Update a body-map marker",
)
def update_marker(
    marker_id: int, payload: BodyMapMarkerUpdate, db=Depends(get_db)
) -> BodyMapMarkerOut:
    return bodymap_service.update_marker(db, marker_id, payload)


@router.delete(
    "/markers/{marker_id}",
    status_code=204,
    summary="Delete a body-map marker",
)
def delete_marker(marker_id: int, db=Depends(get_db)) -> None:
    bodymap_service.delete_marker(db, marker_id)
