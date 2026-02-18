from __future__ import annotations

from typing import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.ml.processor import ImageProcessor


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_processor(request: Request) -> ImageProcessor:
    """Return the shared ImageProcessor stored in app.state."""
    return request.app.state.processor
