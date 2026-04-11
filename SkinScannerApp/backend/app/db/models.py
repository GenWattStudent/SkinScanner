from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ScanResult(Base):
    """One row per completed scan (shared across all models)."""

    __tablename__ = "scan_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Consensus (aggregated across all models)
    consensus_class_key: Mapped[str] = mapped_column(String(100), nullable=False)
    consensus_risk_level: Mapped[int] = mapped_column(Integer, nullable=False)
    consensus_confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Original image file on disk
    original_image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Per-model results (children)
    model_results: Mapped[list["ModelResultRow"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan", lazy="joined"
    )


class ModelResultRow(Base):
    """One row per model per scan — stores per-model prediction + heatmap."""

    __tablename__ = "model_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scan_results.id", ondelete="CASCADE"), nullable=False
    )

    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_label: Mapped[str] = mapped_column(String(100), nullable=False)

    # Top-1 prediction
    class_key: Mapped[str] = mapped_column(String(100), nullable=False)
    class_pl: Mapped[str] = mapped_column(String(100), nullable=False)
    class_en: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Serialised top-3 as JSON string: '[{"class_key":…,"confidence":…}, …]'
    top3_json: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Heatmap image file on disk
    heatmap_image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    scan: Mapped["ScanResult"] = relationship(back_populates="model_results")


class Patient(Base):
    """A patient whose body map markers are tracked individually."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Children
    markers: Mapped[list["BodyMapMarker"]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", lazy="selectin"
    )


class BodyMapMarker(Base):
    """A pin placed on the body diagram to track a lesion location."""

    __tablename__ = "body_map_markers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Normalised position on the body SVG (0.0–1.0 range)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)

    # Which view of the body the marker belongs to
    view: Mapped[str] = mapped_column(String(10), nullable=False, default="front")

    # User-defined label / description
    label: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional link to a scan result
    scan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("scan_results.id", ondelete="SET NULL"), nullable=True
    )

    # Owning patient
    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    patient: Mapped["Patient"] = relationship(back_populates="markers")
