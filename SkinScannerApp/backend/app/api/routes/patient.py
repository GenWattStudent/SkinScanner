"""
REST routes for the Patient feature.

Endpoints
─────────
GET    /patients         → list all patients
POST   /patients         → create a patient
GET    /patients/{id}    → get a single patient
PATCH  /patients/{id}    → update a patient
DELETE /patients/{id}    → delete a patient (cascades markers)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.schemas.patient import (
    PatientCreate,
    PatientList,
    PatientOut,
    PatientUpdate,
)
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get(
    "",
    response_model=PatientList,
    summary="List all patients",
)
def list_patients(db=Depends(get_db)) -> PatientList:
    return patient_service.list_patients(db)


@router.post(
    "",
    response_model=PatientOut,
    status_code=201,
    summary="Create a patient",
)
def create_patient(payload: PatientCreate, db=Depends(get_db)) -> PatientOut:
    return patient_service.create_patient(db, payload)


@router.get(
    "/{patient_id}",
    response_model=PatientOut,
    summary="Get a single patient",
)
def get_patient(patient_id: int, db=Depends(get_db)) -> PatientOut:
    patient = patient_service.get_patient(db, patient_id)
    return patient_service._to_schema(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientOut,
    summary="Update a patient",
)
def update_patient(
    patient_id: int, payload: PatientUpdate, db=Depends(get_db)
) -> PatientOut:
    return patient_service.update_patient(db, patient_id, payload)


@router.delete(
    "/{patient_id}",
    status_code=204,
    summary="Delete a patient (cascades to markers)",
)
def delete_patient(patient_id: int, db=Depends(get_db)) -> None:
    patient_service.delete_patient(db, patient_id)
