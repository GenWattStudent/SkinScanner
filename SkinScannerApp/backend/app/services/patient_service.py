"""
CRUD operations for Patient.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy.orm import Session

from app.db.models import Patient
from app.core.exceptions import PatientNotFoundError
from app.schemas.patient import (
    PatientCreate,
    PatientList,
    PatientOut,
    PatientUpdate,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _to_schema(patient: Patient) -> PatientOut:
    return PatientOut(
        id=patient.id,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
        name=patient.name,
        notes=patient.notes,
        marker_count=len(patient.markers),
    )


# ── Public API ───────────────────────────────────────────────────────────────

def list_patients(db: Session) -> PatientList:
    """Return all patients ordered by name."""
    items = db.query(Patient).order_by(Patient.name.asc()).all()
    return PatientList(total=len(items), items=[_to_schema(p) for p in items])


def get_patient(db: Session, patient_id: int) -> Patient:
    """Fetch a single patient or raise."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise PatientNotFoundError(patient_id)
    return patient


def create_patient(db: Session, payload: PatientCreate) -> PatientOut:
    """Insert a new patient row."""
    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    logger.info(f"Created patient id={patient.id} name={patient.name!r}")
    return _to_schema(patient)


def update_patient(
    db: Session, patient_id: int, payload: PatientUpdate
) -> PatientOut:
    """Partially update an existing patient."""
    patient = get_patient(db, patient_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    logger.info(f"Updated patient id={patient.id}")
    return _to_schema(patient)


def delete_patient(db: Session, patient_id: int) -> None:
    """Delete a patient by ID (cascades to their markers)."""
    patient = get_patient(db, patient_id)
    db.delete(patient)
    db.commit()
    logger.info(f"Deleted patient id={patient_id}")
