from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import analyze, camera, health, history

# ── REST router (mounted at /api/v1) ─────────────────────────────────────────
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(analyze.router)
api_router.include_router(history.router)

# ── WebSocket router (mounted at /ws) ────────────────────────────────────────
ws_router = APIRouter()
ws_router.include_router(camera.router)
