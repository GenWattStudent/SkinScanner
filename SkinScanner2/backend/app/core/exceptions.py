from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


# ── Custom exception types ───────────────────────────────────────────────────

class ModelNotLoadedError(Exception):
    def __init__(self, model_type: str) -> None:
        self.model_type = model_type
        super().__init__(f"Model '{model_type}' is not loaded or unavailable.")


class ImageProcessingError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class HistoryEntryNotFoundError(Exception):
    def __init__(self, entry_id: int) -> None:
        self.entry_id = entry_id
        super().__init__(f"History entry with id={entry_id} not found.")


# ── FastAPI exception handlers ───────────────────────────────────────────────

async def model_not_loaded_handler(
    request: Request, exc: ModelNotLoadedError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"code": "MODEL_NOT_LOADED", "message": str(exc)},
    )


async def image_processing_handler(
    request: Request, exc: ImageProcessingError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"code": "IMAGE_PROCESSING_ERROR", "message": exc.detail},
    )


async def history_not_found_handler(
    request: Request, exc: HistoryEntryNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"code": "HISTORY_ENTRY_NOT_FOUND", "message": str(exc)},
    )
