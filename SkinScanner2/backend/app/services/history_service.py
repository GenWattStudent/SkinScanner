"""
CRUD operations for ScanResult history (multi-model aware).
"""
from __future__ import annotations

import json
from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session

from app.core.exceptions import HistoryEntryNotFoundError
from app.db.models import ModelResultRow, ScanResult
from app.schemas.history import HistoryEntry, HistoryList, ModelResultEntry


# ── Helpers ──────────────────────────────────────────────────────────────────

def _entry_url(entry_id: int, kind: str) -> str:
    return f"/api/v1/history/{entry_id}/image/{kind}"


def _model_heatmap_url(entry_id: int, model_type: str) -> str:
    return f"/api/v1/history/{entry_id}/image/heatmap/{model_type}"


def _to_schema(item: ScanResult) -> HistoryEntry:
    model_entries: list[ModelResultEntry] = []
    for mr in item.model_results:
        try:
            top3 = json.loads(mr.top3_json) if mr.top3_json else None
        except Exception:
            top3 = None

        model_entries.append(
            ModelResultEntry(
                model_type=mr.model_type,
                model_label=mr.model_label,
                class_key=mr.class_key,
                class_pl=mr.class_pl,
                class_en=mr.class_en,
                confidence=mr.confidence,
                risk_level=mr.risk_level,
                top3=top3,
                image_heatmap_url=(
                    _model_heatmap_url(item.id, mr.model_type)
                    if mr.heatmap_image_path
                    else None
                ),
            )
        )

    return HistoryEntry(
        id=item.id,
        timestamp=item.timestamp,
        consensus_class_key=item.consensus_class_key,
        consensus_risk_level=item.consensus_risk_level,
        consensus_confidence=item.consensus_confidence,
        model_results=model_entries,
        image_original_url=(
            _entry_url(item.id, "original") if item.original_image_path else None
        ),
    )


# ── Public API ────────────────────────────────────────────────────────────────

def get_history(db: Session, *, page: int = 1, limit: int = 20) -> HistoryList:
    total: int = db.query(ScanResult).count()
    items = (
        db.query(ScanResult)
        .order_by(ScanResult.timestamp.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return HistoryList(
        total=total,
        page=page,
        limit=limit,
        items=[_to_schema(item) for item in items],
    )


def get_entry(db: Session, entry_id: int) -> ScanResult:
    entry = db.query(ScanResult).filter(ScanResult.id == entry_id).first()
    if entry is None:
        raise HistoryEntryNotFoundError(entry_id)
    return entry


def delete_entry(db: Session, entry_id: int) -> None:
    entry = get_entry(db, entry_id)

    # Remove original image from disk
    if entry.original_image_path:
        p = Path(entry.original_image_path)
        if p.exists():
            p.unlink()
            logger.info(f"Deleted image: {p}")

    # Remove per-model heatmap images from disk
    for mr in entry.model_results:
        if mr.heatmap_image_path:
            p = Path(mr.heatmap_image_path)
            if p.exists():
                p.unlink()
                logger.info(f"Deleted heatmap: {p}")

    db.delete(entry)
    db.commit()
    logger.info(f"Deleted history entry id={entry_id}")
