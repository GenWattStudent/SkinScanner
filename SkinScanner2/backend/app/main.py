"""
FastAPI application factory.

Startup sequence
────────────────
  1. Configure loguru (stdout + rotating file)
  2. Create SQLite tables (idempotent)
  3. Load all four PyTorch models into app.state.models
  4. Instantiate the shared ImageProcessor → app.state.processor
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.router import api_router, ws_router
from app.core.config import DEVICE, settings
from app.core.exceptions import (
    HistoryEntryNotFoundError,
    ImageProcessingError,
    MarkerNotFoundError,
    ModelNotLoadedError,
    PatientNotFoundError,
    history_not_found_handler,
    image_processing_handler,
    marker_not_found_handler,
    model_not_loaded_handler,
    patient_not_found_handler,
)
from app.core.logging import setup_logging
from app.db.database import create_tables
from app.ml.loader import ModelLoader
from app.ml.processor import ImageProcessor


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # ── Startup ──────────────────────────────────────────────────────────────
    setup_logging()
    logger.info("━━━━━━━━━━━━━━━━━━━━  SkinScanner API  ━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"Device : {DEVICE}")
    logger.info(f"Models : {settings.models_dir}")
    logger.info(f"DB     : {settings.db_url}")

    create_tables()
    logger.info("Database tables ready")

    loader = ModelLoader()
    app.state.models = loader.load_all()
    app.state.processor = ImageProcessor()

    logger.info("API ready  🩺")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("SkinScanner API shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="SkinScanner API",
        version="1.0.0",
        description=(
            "AI-powered skin lesion classification. "
            "Supports MobileNetV3, ResNet-50, ViT B/16, and a custom CNN baseline. "
            "Provides Grad-CAM explainability heatmaps and persistent scan history."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ───────────────────────────────────────────────────
    app.add_exception_handler(ModelNotLoadedError, model_not_loaded_handler)          # type: ignore[arg-type]
    app.add_exception_handler(ImageProcessingError, image_processing_handler)         # type: ignore[arg-type]
    app.add_exception_handler(HistoryEntryNotFoundError, history_not_found_handler)   # type: ignore[arg-type]
    app.add_exception_handler(MarkerNotFoundError, marker_not_found_handler)          # type: ignore[arg-type]
    app.add_exception_handler(PatientNotFoundError, patient_not_found_handler)        # type: ignore[arg-type]

    # ── Routers ──────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(ws_router, prefix="/ws")

    return app


app = create_app()
