import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure loguru: pretty stdout + rotating file."""
    logger.remove()

    # ── Console ─────────────────────────────────────────────────────────────
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> – <level>{message}</level>"
        ),
        level="INFO",
        colorize=True,
    )

    # ── File (rotating) ─────────────────────────────────────────────────────
    log_path: Path = settings.logs_dir / "skinscanner.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} – {message}",
        encoding="utf-8",
    )
