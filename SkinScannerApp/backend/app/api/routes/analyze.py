from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, UploadFile

from app.api.deps import get_db, get_processor
from app.ml.processor import ImageProcessor
from app.schemas.analyze import AnalyzeResponse
from app.services.analyze_service import run_analysis

router = APIRouter(tags=["Analyze"])

# All ML inference is CPU/GPU-bound and synchronous.
# FastAPI automatically runs sync def routes in a threadpool,
# keeping the event loop free.


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyse a skin lesion image with ALL loaded models",
    description=(
        "Upload a JPEG/PNG image and receive predictions from every loaded model, "
        "Grad-CAM heatmaps per model, consensus diagnosis, and the persisted scan ID."
    ),
)
def analyze(
    request: Request,
    file: UploadFile,
    crop_factor: float = Form(
        default=0.0,
        ge=0.0,
        le=0.5,
        description="Symmetrically crop each edge by this fraction (0 = no crop)",
    ),
    auto_focus: bool = Form(
        default=False,
        description="Clear background and auto-zoom into the dominant lesion ROI",
    ),
    db=Depends(get_db),
    processor: ImageProcessor = Depends(get_processor),
) -> AnalyzeResponse:
    models: dict = request.app.state.models
    if not models:
        from app.core.exceptions import ModelNotLoadedError
        raise ModelNotLoadedError("No models loaded")

    image_bytes: bytes = file.file.read()

    return run_analysis(
        image_bytes=image_bytes,
        models=models,
        crop_factor=crop_factor,
        auto_focus=auto_focus,
        processor=processor,
        db=db,
    )
