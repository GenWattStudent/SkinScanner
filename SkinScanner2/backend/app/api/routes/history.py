from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from app.api.deps import get_db
from app.schemas.history import HistoryEntry, HistoryList
from app.services import history_service

router = APIRouter(tags=["History"])


@router.get(
    "/history",
    response_model=HistoryList,
    summary="List scan history (paginated, newest first)",
)
def list_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_db),
) -> HistoryList:
    return history_service.get_history(db, page=page, limit=limit)


@router.get(
    "/history/{entry_id}",
    response_model=HistoryEntry,
    summary="Get a single history entry by ID",
)
def get_entry(entry_id: int, db=Depends(get_db)) -> HistoryEntry:
    record = history_service.get_entry(db, entry_id)
    return history_service._to_schema(record)


@router.delete(
    "/history/{entry_id}",
    status_code=204,
    summary="Delete a history entry and its images",
)
def delete_entry(entry_id: int, db=Depends(get_db)) -> None:
    history_service.delete_entry(db, entry_id)


@router.get(
    "/history/{entry_id}/image/original",
    summary="Stream the original image for a history entry",
    responses={200: {"content": {"image/png": {}}}},
)
def get_original_image(entry_id: int, db=Depends(get_db)) -> FileResponse:
    record = history_service.get_entry(db, entry_id)
    path_str = record.original_image_path
    if not path_str or not Path(path_str).exists():
        raise HTTPException(status_code=404, detail="Original image file not found on disk")
    return FileResponse(path_str, media_type="image/png")


@router.get(
    "/history/{entry_id}/image/heatmap/{model_type}",
    summary="Stream a per-model heatmap image for a history entry",
    responses={200: {"content": {"image/png": {}}}},
)
def get_heatmap_image(entry_id: int, model_type: str, db=Depends(get_db)) -> FileResponse:
    record = history_service.get_entry(db, entry_id)
    for mr in record.model_results:
        if mr.model_type == model_type:
            if mr.heatmap_image_path and Path(mr.heatmap_image_path).exists():
                return FileResponse(mr.heatmap_image_path, media_type="image/png")
            break
    raise HTTPException(status_code=404, detail=f"Heatmap not found for model '{model_type}'")
