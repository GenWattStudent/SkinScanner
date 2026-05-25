# Ensemble Pipeline – Dokumentacja

## Pliki

| Plik | Rola |
|---|---|
| `check_ensemble.py` | Ładuje modele, testuje wszystkie kombinacje, zapisuje `ensemble_results.json` |
| `class_meta.py` | Słownik klas: tłumaczenia PL/EN, wariant choroby, emoji, opis |
| `analyze_ensemble.py` | **Czyta JSON** (bez GPU/modeli), analizuje per wariant |

---

## Schemat użycia

```
                  ┌─────────────────────────┐
                  │    check_ensemble.py     │  ← potrzebne GPU + modele .pth
                  │   (uruchamiaj raz)       │    ~5–15 min
                  └────────────┬────────────┘
                               │ generuje
                               ▼
                  ┌─────────────────────────┐
                  │  ensemble_results.json   │  ← plik wynikowy (~1 MB)
                  └────────────┬────────────┘
                               │ czyta
                               ▼
                  ┌─────────────────────────┐
                  │   analyze_ensemble.py    │  ← działa natychmiast, bez GPU
                  │   + class_meta.py        │    ~1 sekunda
                  └─────────────────────────┘
```

---

## Krok 1 – Generowanie wyników (raz)

```bash
python check_ensemble.py
```

Wymaga:
- folderu `models/` z plikami `*_best.pth`
- folderu `assets/images/test/` w strukturze ImageFolder (`test/<klasa>/<obrazy>`)
- GPU (opcjonalnie, ale przyspiesza ~10×)

Tworzy: `ensemble_results.json`, `ensemble_log.txt`

---

## Krok 2 – Analiza per wariant (wielokrotnie, bez GPU)

```bash
# Podstawowe użycie
python analyze_ensemble.py

# Inny plik wyników
python analyze_ensemble.py --results ensemble_results.json

# Pokaż top-5 kombinacji na wariant (domyślnie 3)
python analyze_ensemble.py --top 5

# Zapisz raport TXT + CSV
python analyze_ensemble.py --top 5 --save-report
```

---

## Co pokazuje analyze_ensemble.py

### 1. Słownik klas
```
 #  EN (folder)                          PL                          Wariant                  Emoji
 1  Actinic keratoses                    Rogowacenie słoneczne        Przednowotworowe          ☀️
 2  Basal cell carcinoma                 Rak podstawnokomórkowy       Nowotworowe (rak skóry)   🔴
...
```

### 2. Globalne top kombinacje (overall accuracy)

### 3. Ranking per wariant
Dla każdej grupy (Wirusowe / Nowotworowe / Łagodne / …):
- TOP N kombinacji posortowanych wg. **średniej accuracy klas w tym wariancie**
- Per-klasa dla najlepszej kombinacji w wariancie z paskiem procentowym

### 4. Podsumowanie końcowe
Jedna linia per wariant: najlepsza kombinacja + accuracy

---

## Warianty chorób

| Wariant | Klasy |
|---|---|
| ☀️ Przednowotworowe | Actinic keratoses |
| 🔴 Nowotworowe (rak skóry) | Basal cell carcinoma, Melanoma, Squamous cell carcinoma |
| 🟡 Łagodne | Benign keratosis-like lesions, Dermatofibroma, Melanocytic nevi |
| 🦠 Wirusowe | Chickenpox, Cowpox, HFMD, Measles, Monkeypox |
| ✅ Zdrowe | Healthy |
| 💜 Naczyniowe / Łagodne | Vascular lesions |

---

## Dodawanie nowej klasy do class_meta.py

```python
"Nowa klasa": {
    "pl":         "Polska nazwa",
    "en":         "English name",
    "variant":    "Wariant PL",       # musi pasować do istniejącej grupy lub nowa
    "variant_en": "Variant EN",
    "emoji":      "🟠",
    "desc_pl":    "Krótki opis po polsku.",
    "desc_en":    "Short description in English.",
},
```

---

## Struktura ensemble_results.json

```json
{
  "generated_at": "2025-01-01T12:00:00",
  "device": "cuda",
  "dataset_size": 1400,
  "num_classes": 14,
  "classes": ["Actinic keratoses", ...],
  "best_single_model": "EfficientNet",
  "best_single_model_acc": 87.14,
  "best_ensemble_combo": ["EfficientNet", "ViT"],
  "best_ensemble_acc": 90.21,
  "gain_vs_single": 3.07,
  "all_results": [
    {
      "combination": ["EfficientNet", "ViT"],
      "n_models": 2,
      "accuracy": 90.21,
      "per_class": {
        "Actinic keratoses": 85.0,
        "Melanoma": 92.5,
        ...
      }
    },
    ...
  ]
}
```