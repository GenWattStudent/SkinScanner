"""
Convenience launcher — run from the backend/ directory:

    python run.py
    # or
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import sys
from pathlib import Path

# Ensure the backend/ directory is on sys.path so `app.*` imports work
# regardless of the CWD from which this script is invoked.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import uvicorn  # noqa: E402
from app.core.config import settings  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        reload_dirs=[str(_HERE)],
        log_config=None,  # loguru handles all logging
    )
