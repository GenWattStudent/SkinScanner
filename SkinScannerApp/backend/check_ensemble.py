"""
Ensemble (Bagging) Comparison  –  check_ensemble.py
=====================================================
Sprawdza WSZYSTKIE możliwe kombinacje 5 wytrenowanych modeli
i loguje dokładność każdej z nich (posortowaną od najlepszej).

Architektury zgodne z notebook-trening.ipynb:
  • CustomCNN    – 3x (Conv→ReLU→MaxPool) + Flatten→512→num_classes
  • ResNet50     – torchvision resnet50, fc → num_classes
  • MobileNetV3  – mobilenet_v3_LARGE, classifier[3] → num_classes
  • ViT          – vit_b_16,            heads.head  → num_classes
  • EfficientNet – efficientnet_b0,     classifier[1] → num_classes

Uruchomienie:
    python check_ensemble.py

Wymagania:
    pip install torch torchvision pillow loguru
"""

import os
import sys
import json
import time
import itertools
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms, models, datasets
from torch.utils.data import DataLoader
from loguru import logger

# ─── CONFIG ───────────────────────────────────────────────────────────────────

MODELS_DIR   = Path("../models")
DATA_DIR     = Path("../assets/images/test")   # ImageFolder – podfolderami są nazwy klas
RESULTS_FILE = Path("ensemble_results.json")
LOG_FILE     = Path("ensemble_log.txt")

DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 32
IMG_SIZE   = 224

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logger.remove()
logger.add(
    sys.stdout, colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
)
logger.add(LOG_FILE, format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
           rotation="10 MB")

# ─── DATASET ──────────────────────────────────────────────────────────────────

TEST_TRANSFORM = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def build_loader(data_dir: Path) -> tuple[DataLoader, list[str]]:
    """ImageFolder – podfolderami są nazwy klas (tak jak w notebooku)."""
    dataset     = datasets.ImageFolder(str(data_dir), transform=TEST_TRANSFORM)
    class_names = dataset.classes
    loader      = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=0, pin_memory=(DEVICE.type == "cuda"))
    logger.info(f"Dataset: {len(dataset)} obrazów | {len(class_names)} klas")
    logger.info(f"Klasy: {class_names}")
    return loader, class_names


# ─── MODEL DEFINITIONS  (zgodnie z notebook-trening.ipynb) ────────────────────

class CustomCNN(nn.Module):
    """Identyczna z notebookiem: 3x (Conv→ReLU→MaxPool) + MLP."""

    def __init__(self, num_classes: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        flat = 128 * (IMG_SIZE // 8) * (IMG_SIZE // 8)   # 128 * 28 * 28 = 100352
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(flat, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def _build_resnet50(n: int) -> nn.Module:
    m = models.resnet50(weights=None)
    m.fc = nn.Linear(m.fc.in_features, n)
    return m


def _build_mobilenet_v3_large(n: int) -> nn.Module:
    """Notebook używa mobilenet_v3_LARGE (nie small!)."""
    m = models.mobilenet_v3_large(weights=None)
    m.classifier[3] = nn.Linear(m.classifier[3].in_features, n)
    return m


def _build_vit(n: int) -> nn.Module:
    m = models.vit_b_16(weights=None)
    m.heads.head = nn.Linear(m.heads.head.in_features, n)
    return m


def _build_efficientnet_b0(n: int) -> nn.Module:
    m = models.efficientnet_b0(weights=None)
    m.classifier[1] = nn.Linear(m.classifier[1].in_features, n)
    return m


# ─── MODEL REGISTRY ───────────────────────────────────────────────────────────

def get_registry(num_classes: int) -> dict[str, tuple]:
    return {
        "CustomCNN":    (lambda: CustomCNN(num_classes),                MODELS_DIR / "CustomCNN_best.pth"),
        "EfficientNet": (lambda: _build_efficientnet_b0(num_classes),   MODELS_DIR / "EfficientNet_best.pth"),
        "MobileNetV3":  (lambda: _build_mobilenet_v3_large(num_classes),MODELS_DIR / "MobileNetV3_best.pth"),
        "ResNet50":     (lambda: _build_resnet50(num_classes),          MODELS_DIR / "ResNet50_best.pth"),
        "ViT":          (lambda: _build_vit(num_classes),               MODELS_DIR / "ViT_best.pth"),
    }


# ─── LOAD MODEL ───────────────────────────────────────────────────────────────

def load_model(name: str, build_fn, ckpt_path: Path) -> nn.Module | None:
    if not ckpt_path.exists():
        logger.error(f"Brak pliku wag: {ckpt_path}")
        return None

    model = build_fn()

    try:
        state = torch.load(ckpt_path, map_location=DEVICE, weights_only=True)
    except TypeError:
        state = torch.load(ckpt_path, map_location=DEVICE)

    # Obsługa różnych formatów checkpointu
    if isinstance(state, dict):
        for key in ("model_state_dict", "state_dict"):
            if key in state:
                state = state[key]
                break

    # Usuń prefiks "module." jeśli model był trenowany z DataParallel
    new_state = {k.replace("module.", "", 1): v for k, v in state.items()}

    try:
        model.load_state_dict(new_state, strict=True)
    except RuntimeError as e:
        logger.warning(f"{name}: strict=True nie zadziałało ({e}), próbuję strict=False")
        try:
            model.load_state_dict(new_state, strict=False)
        except Exception as e2:
            logger.error(f"Nie udało się załadować {name}: {e2}")
            return None

    model.eval()
    model.to(DEVICE)
    logger.success(f"Załadowano  {name:15s}  <-  {ckpt_path.name}")
    return model


# ─── INFERENCE ────────────────────────────────────────────────────────────────

@torch.no_grad()
def collect_logits(model: nn.Module, loader: DataLoader) -> tuple[np.ndarray, np.ndarray]:
    """Zwraca (logits [N, C], labels [N])."""
    all_logits, all_labels = [], []
    for imgs, labels in loader:
        imgs = imgs.to(DEVICE)
        out  = model(imgs)
        all_logits.append(out.cpu().numpy())
        all_labels.append(labels.numpy())
    return np.concatenate(all_logits), np.concatenate(all_labels)


def ensemble_accuracy(logits_list: list[np.ndarray], labels: np.ndarray) -> float:
    """Average-probability ensemble -> accuracy."""
    probs = [F.softmax(torch.tensor(l), dim=-1).numpy() for l in logits_list]
    avg   = np.mean(probs, axis=0)
    preds = np.argmax(avg, axis=1)
    return float((preds == labels).mean())


def per_class_acc(logits_list: list[np.ndarray],
                  labels: np.ndarray,
                  class_names: list[str]) -> dict:
    probs = [F.softmax(torch.tensor(l), dim=-1).numpy() for l in logits_list]
    avg   = np.mean(probs, axis=0)
    preds = np.argmax(avg, axis=1)
    return {
        cls: (round(float((preds[labels == i] == labels[labels == i]).mean()) * 100, 2)
              if (labels == i).sum() > 0 else None)
        for i, cls in enumerate(class_names)
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 72)
    logger.info(f"  Ensemble Bagging Comparison   |  device = {DEVICE}")
    logger.info(f"  Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 72)

    # 1. Dataset
    if not DATA_DIR.exists():
        logger.critical(f"Brak katalogu z danymi: {DATA_DIR}")
        sys.exit(1)

    loader, class_names = build_loader(DATA_DIR)
    num_classes = len(class_names)

    if len(loader.dataset) == 0:
        logger.critical("Dataset jest pusty – sprawdź ścieżkę.")
        sys.exit(1)

    # 2. Załaduj modele
    registry = get_registry(num_classes)
    loaded: dict[str, nn.Module] = {}

    for name, (build_fn, ckpt) in registry.items():
        m = load_model(name, build_fn, ckpt)
        if m is not None:
            loaded[name] = m

    if not loaded:
        logger.critical("Nie udało się załadować żadnego modelu.")
        sys.exit(1)

    logger.info(f"\nZaładowane ({len(loaded)}): {list(loaded.keys())}\n")

    # 3. Oblicz logity – raz dla każdego modelu
    logger.info("Obliczanie logitów…")
    model_logits: dict[str, np.ndarray] = {}
    labels_ref: np.ndarray | None = None

    for name, model in loaded.items():
        t0 = time.time()
        logits, labels = collect_logits(model, loader)
        model_logits[name] = logits
        if labels_ref is None:
            labels_ref = labels

        single_acc = float((np.argmax(logits, axis=1) == labels).mean())
        logger.info(f"  {name:15s}  single-model = {single_acc*100:6.2f}%  ({time.time()-t0:.1f}s)")

    logger.info("")

    # 4. Wszystkie kombinacje (2..N modeli)
    names = list(model_logits.keys())
    results: list[dict] = []

    # Pojedyncze modele
    for n in names:
        acc = float((np.argmax(model_logits[n], axis=1) == labels_ref).mean())
        results.append({
            "combination": [n],
            "n_models": 1,
            "accuracy": round(acc * 100, 4),
            "per_class": per_class_acc([model_logits[n]], labels_ref, class_names),
        })

    total_combos = sum(
        len(list(itertools.combinations(names, r)))
        for r in range(2, len(names) + 1)
    )
    logger.info(f"Sprawdzam {total_combos} kombinacji ensembli…")

    checked = 0
    for r in range(2, len(names) + 1):
        for combo in itertools.combinations(names, r):
            ll  = [model_logits[n] for n in combo]
            acc = ensemble_accuracy(ll, labels_ref)
            results.append({
                "combination": list(combo),
                "n_models": r,
                "accuracy": round(acc * 100, 4),
                "per_class": per_class_acc(ll, labels_ref, class_names),
            })
            checked += 1
            if checked % 5 == 0:
                logger.debug(f"  {checked}/{total_combos} kombinacji…")

    # 5. Sortuj od najlepszej
    results.sort(key=lambda x: x["accuracy"], reverse=True)

    single_best_acc  = max(r["accuracy"] for r in results if r["n_models"] == 1)
    single_best_name = next(
        r["combination"][0] for r in results
        if r["n_models"] == 1 and r["accuracy"] == single_best_acc
    )

    # 6. Wyświetl tabelę
    logger.info("")
    logger.info("=" * 72)
    logger.info("  WYNIKI  –  posortowane od najlepszej kombinacji")
    logger.info("=" * 72)
    logger.info(f"  {'#':>3}  {'N':>2}  {'Acc':>7}  {'Delta':>7}  Kombinacja")
    logger.info(f"  {'-'*3}  {'-'*2}  {'-'*7}  {'-'*7}  {'-'*30}")

    best_acc = results[0]["accuracy"]

    for rank, res in enumerate(results, 1):
        combo = " + ".join(res["combination"])
        n     = res["n_models"]
        acc   = res["accuracy"]
        delta = acc - single_best_acc

        if acc == best_acc and n > 1:
            tag = "  NAJLEPSZA ENSEMBLE"
        elif n == 1 and acc == single_best_acc:
            tag = "  NAJLEPSZY SINGLE"
        elif delta > 0:
            tag = f"  +{delta:.2f}%"
        elif delta == 0:
            tag = "  ="
        else:
            tag = f"  {delta:.2f}%"

        logger.info(f"  #{rank:>3}  {n:>2}M  {acc:>6.2f}%  {delta:>+7.2f}%  {combo}{tag}")

    logger.info("")
    logger.info("-" * 72)
    logger.info(f"  Najlepszy single model  : {single_best_name}  ->  {single_best_acc:.2f}%")
    logger.info(f"  Najlepsza kombinacja    : {' + '.join(results[0]['combination'])}  ->  {results[0]['accuracy']:.2f}%")
    logger.info(f"  Zysk z ensemblingu      : +{results[0]['accuracy'] - single_best_acc:.2f}%")
    logger.info("-" * 72)

    # 7. Per-class dla TOP 3
    logger.info("\n  TOP-3 – dokladnosc per-klasa:\n")
    for rank, res in enumerate(results[:3], 1):
        combo = " + ".join(res["combination"])
        logger.info(f"  #{rank} {combo}  ({res['accuracy']:.2f}%)")
        for cls, v in res["per_class"].items():
            bar = "#" * int((v or 0) / 5)
            val = f"{v:.1f}%" if v is not None else "brak danych"
            logger.info(f"      {cls:<35s} {val:>6}  {bar}")
        logger.info("")

    # 8. Zapis JSON
    output = {
        "generated_at":           datetime.now().isoformat(),
        "device":                 str(DEVICE),
        "dataset_path":           str(DATA_DIR),
        "dataset_size":           len(loader.dataset),
        "num_classes":            num_classes,
        "classes":                class_names,
        "best_single_model":      single_best_name,
        "best_single_model_acc":  single_best_acc,
        "best_ensemble_combo":    results[0]["combination"],
        "best_ensemble_acc":      results[0]["accuracy"],
        "gain_vs_single":         round(results[0]["accuracy"] - single_best_acc, 4),
        "all_results":            results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.success(f"Wyniki JSON  ->  {RESULTS_FILE}")
    logger.success(f"Log          ->  {LOG_FILE}")
    logger.info(f"Koniec: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()