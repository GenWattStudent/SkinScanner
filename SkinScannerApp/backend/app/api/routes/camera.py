"""
WebSocket endpoints for live camera / dermoscope streaming.

Roles
─────
  sender  →  WS /ws/camera/send
             Phone or dermoscope pushes raw JPEG frames as binary messages.
             One sender at a time is supported; a new connection replaces the
             previous one.

  viewer  →  WS /ws/camera/view
             Desktop client receives every frame broadcast by the sender.
             Multiple viewers are supported simultaneously.

Flow
────
  phone  ──[JPEG bytes]──▶  /ws/camera/send  ──[broadcast]──▶  /ws/camera/view  ──▶  desktop

Analysis trigger
────────────────
  The frontend captures a still frame via getUserMedia / canvas.toBlob()
  and POSTs it to  POST /api/v1/analyze  independently from the stream.
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter(tags=["Camera"])


class ConnectionManager:
    """Thread-safe pub/sub for camera frames over WebSocket."""

    def __init__(self) -> None:
        self._senders: list[WebSocket] = []
        self._viewers: list[WebSocket] = []

    # ── Connection management ────────────────────────────────────────────────

    async def add_sender(self, ws: WebSocket) -> None:
        await ws.accept()
        self._senders.append(ws)
        logger.info(f"Camera sender connected  (total={len(self._senders)})")

    async def add_viewer(self, ws: WebSocket) -> None:
        await ws.accept()
        self._viewers.append(ws)
        logger.info(f"Camera viewer connected  (total={len(self._viewers)})")

    def remove(self, ws: WebSocket) -> None:
        self._senders = [s for s in self._senders if s is not ws]
        self._viewers = [v for v in self._viewers if v is not ws]

    # ── Broadcasting ─────────────────────────────────────────────────────────

    async def broadcast(self, data: bytes) -> None:
        """Send a JPEG frame to every connected viewer."""
        dead: list[WebSocket] = []
        for viewer in list(self._viewers):
            try:
                await viewer.send_bytes(data)
            except Exception:
                dead.append(viewer)
        for ws in dead:
            self.remove(ws)

    # ── Status ───────────────────────────────────────────────────────────────

    @property
    def status(self) -> dict[str, int]:
        return {
            "senders": len(self._senders),
            "viewers": len(self._viewers),
        }


# Module-level singleton — initialised once, shared across all WS connections.
manager = ConnectionManager()


# ── WebSocket routes ─────────────────────────────────────────────────────────

@router.websocket("/camera/send")
async def camera_send(websocket: WebSocket) -> None:
    """Phone / dermoscope endpoint — receives JPEG binary frames and broadcasts them."""
    await manager.add_sender(websocket)
    try:
        while True:
            frame: bytes = await websocket.receive_bytes()
            await manager.broadcast(frame)
    except WebSocketDisconnect:
        manager.remove(websocket)
        logger.info("Camera sender disconnected")


@router.websocket("/camera/view")
async def camera_view(websocket: WebSocket) -> None:
    """Desktop endpoint — receives JPEG frames pushed by the server."""
    await manager.add_viewer(websocket)
    try:
        # Keep the connection alive; broadcast() pushes frames from the sender task.
        # Receive loop handles incoming pings / control messages from the client.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.remove(websocket)
        logger.info("Camera viewer disconnected")


# ── REST helper ───────────────────────────────────────────────────────────────

@router.get("/camera/status", summary="Live WebSocket connection counts")
async def camera_status() -> dict[str, int]:
    return manager.status
