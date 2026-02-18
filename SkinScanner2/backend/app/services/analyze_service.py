"""
Orchestrates the full multi-model analysis pipeline:
  image bytes → crop → for each model: preprocess → predict → Grad-CAM
  → encode base64 → persist to disk + DB → return AnalyzeResponse
"""
from __future__ import annotations

import base64
import io
import json
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import torch.nn as nn
from loguru import logger
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ImageProcessingError
from app.db.models import ModelResultRow, ScanResult
from app.ml.constants import CLASSES, DISEASE_INFO
from app.ml.processor import ImageProcessor
from app.schemas.analyze import AnalyzeResponse, ClassPrediction, ModelResult


# ── Human-readable labels ───────────────────────────────────────────────────

MODEL_LABELS: dict[str, str] = {
    "mobilenet": "MobileNetV3",
    "resnet50": "ResNet-50",
    "customcnn": "Custom CNN",
    "vit": "Vision Transformer",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _to_base64(img: np.ndarray | Image.Image) -> str:
    """Encode a PIL Image or uint8 numpy array to a PNG data-URI."""
    if isinstance(img, np.ndarray):
        pil = Image.fromarray(img.astype(np.uint8))
    else:
        pil = img
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


def _apply_crop(image: Image.Image, crop_factor: float) -> Image.Image:
    """Symmetrically crop all four edges by `crop_factor` fraction."""
    if crop_factor <= 0.0:
        return image
    w, h = image.size
    cx = int(w * crop_factor)
    cy = int(h * crop_factor)
    return image.crop((cx, cy, w - cx, h - cy))


def _save_image(img: Image.Image | np.ndarray, path: Path) -> None:
    if isinstance(img, np.ndarray):
        Image.fromarray(img.astype(np.uint8)).save(path)
    else:
        img.save(path)


def _build_predictions(top_probs, top_idx) -> list[ClassPrediction]:
    """Build ClassPrediction list from top-k results."""
    predictions: list[ClassPrediction] = []
    for prob, idx in zip(top_probs, top_idx):
        key = CLASSES[int(idx)]
        info = DISEASE_INFO[key]
        predictions.append(
            ClassPrediction(
                class_key=key,
                class_pl=info["pl"],
                class_en=info["en"],
                confidence=float(prob),
                risk_level=info["risk"],
                description_pl=info["desc_pl"],
                description_en=info["desc_en"],
            )
        )
    return predictions


def _compute_consensus(
    model_results: list[ModelResult],
) -> tuple[str, int, float]:
    """
    Weighted vote across models.
    Returns (class_key, risk_level, average_confidence_for_winner).
    """
    votes: Counter[str] = Counter()
    confidences: dict[str, list[float]] = {}

    for mr in model_results:
        key = mr.primary_prediction.class_key
        conf = mr.primary_prediction.confidence
        votes[key] += 1
        confidences.setdefault(key, []).append(conf)

    winner = votes.most_common(1)[0][0]
    avg_conf = sum(confidences[winner]) / len(confidences[winner])
    risk = DISEASE_INFO[winner]["risk"]
    return winner, risk, avg_conf


# ── Main service function ─────────────────────────────────────────────────────

def run_analysis(
    *,
    image_bytes: bytes,
    models: dict[str, nn.Module],
    crop_factor: float,
    processor: ImageProcessor,
    db: Session,
) -> AnalyzeResponse:
    # 1. Decode image
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ImageProcessingError(f"Cannot decode image: {exc}") from exc

    # 2. Optional crop
    image = _apply_crop(image, crop_factor)

    # 3. Preprocess once (shared tensor)
    try:
        tensor = processor.prepare(image)
    except Exception as exc:
        raise ImageProcessingError(f"Preprocessing failed: {exc}") from exc

    # 4. Persist original image to disk
    images_dir: Path = settings.history_images_dir
    images_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    original_path = images_dir / f"{file_id}_original.png"
    _save_image(image, original_path)
    original_b64 = _to_base64(image)

    # 5. Run each model
    per_model: list[ModelResult] = []
    heatmap_paths: dict[str, str] = {}

    for model_type, model in models.items():
        try:
            top_probs, top_idx = processor.predict(model, tensor, top_k=3)
            heatmap_arr = processor.generate_heatmap(model, tensor, image, model_type)
        except Exception as exc:
            logger.warning(f"Inference failed for [{model_type}]: {exc}")
            continue

        predictions = _build_predictions(top_probs, top_idx)
        heatmap_b64 = _to_base64(heatmap_arr)

        # Save heatmap to disk
        heatmap_path = images_dir / f"{file_id}_heatmap_{model_type}.png"
        _save_image(heatmap_arr, heatmap_path)
        heatmap_paths[model_type] = str(heatmap_path)

        per_model.append(
            ModelResult(
                model_type=model_type,
                model_label=MODEL_LABELS.get(model_type, model_type),
                primary_prediction=predictions[0],
                top_predictions=predictions,
                heatmap_base64=heatmap_b64,
            )
        )

    if not per_model:
        raise ImageProcessingError("All models failed inference")

    # 6. Consensus
    consensus_key, consensus_risk, consensus_conf = _compute_consensus(per_model)

    # 7. Persist to DB
    record = ScanResult(
        timestamp=datetime.utcnow(),
        consensus_class_key=consensus_key,
        consensus_risk_level=consensus_risk,
        consensus_confidence=consensus_conf,
        original_image_path=str(original_path),
    )
    db.add(record)
    db.flush()  # get record.id

    for mr in per_model:
        top3_data = [
            {"class_key": p.class_key, "confidence": p.confidence, "risk_level": p.risk_level}
            for p in mr.top_predictions
        ]
        row = ModelResultRow(
            scan_id=record.id,
            model_type=mr.model_type,
            model_label=mr.model_label,
            class_key=mr.primary_prediction.class_key,
            class_pl=mr.primary_prediction.class_pl,
            class_en=mr.primary_prediction.class_en,
            confidence=mr.primary_prediction.confidence,
            risk_level=mr.primary_prediction.risk_level,
            top3_json=json.dumps(top3_data),
            heatmap_image_path=heatmap_paths.get(mr.model_type),
        )
        db.add(row)

    db.commit()
    db.refresh(record)

    logger.info(
        f"scan_id={record.id} | consensus={consensus_key} "
        f"({consensus_conf:.1%}) | risk={consensus_risk} | "
        f"models={[mr.model_type for mr in per_model]}"
    )

    return AnalyzeResponse(
        scan_id=record.id,
        timestamp=record.timestamp,
        model_results=per_model,
        consensus_class_key=consensus_key,
        consensus_risk_level=consensus_risk,
        consensus_confidence=consensus_conf,
        original_image_base64=original_b64,
    )
