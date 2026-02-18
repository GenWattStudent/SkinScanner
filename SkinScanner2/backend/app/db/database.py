from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.db_url,
    connect_args={"check_same_thread": False},  # required for SQLite
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


def create_tables() -> None:
    """Create all tables (idempotent — safe to call at every startup)."""
    from app.db import models  # noqa: F401 — registers the ORM models
    Base.metadata.create_all(bind=engine)
