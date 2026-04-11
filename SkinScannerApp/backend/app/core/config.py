from __future__ import annotations

from pathlib import Path
from typing import List

import torch
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve workspace layout
# config.py  →  backend/app/core/config.py
_BACKEND_DIR: Path = Path(__file__).resolve().parent.parent.parent   # …/backend/
_ROOT_DIR: Path = _BACKEND_DIR.parent                                 # …/SkinScanner2/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    models_dir: Path = _ROOT_DIR / "models"
    history_images_dir: Path = _ROOT_DIR / "history_images"
    logs_dir: Path = _BACKEND_DIR / "logs"
    db_url: str = "sqlite:///" + str(_BACKEND_DIR / "skinscanner.db").replace("\\", "/")

    # Image
    img_size: int = 224

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = [
        "http://localhost:5173",
        "https://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://*:5173",  # Allow any IP on port 5173 (dev mode)
        "https://*:5173",  # Allow HTTPS from any IP on port 5173
    ]


settings = Settings()

# Computed at startup (not serialised into Settings)
DEVICE: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
