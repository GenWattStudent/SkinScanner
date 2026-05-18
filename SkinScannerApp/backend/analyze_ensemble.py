"""
analyze_ensemble.py  –  Analiza wyników ensemble per wariant choroby
=====================================================================
Czyta gotowy plik  ensemble_results.json  (wygenerowany przez check_ensemble.py)
i NIE wymaga ponownego ładowania modeli / GPU.

Co robi:
  1. Ładuje wyniki z JSON
  2. Dla każdego WARIANTU (wirusowe / nowotworowe / łagodne / …) pokazuje:
       • najlepsze ensemble dla tego wariantu
       • ranking kombinacji modeli wg. avg accuracy na klasach w tym wariancie
  3. Drukuje tabelę z tłumaczeniami PL/EN i emoji dla każdej klasy
  4. Opcjonalnie zapisuje raport do TXT i CSV

Uruchomienie:
    python analyze_ensemble.py                          # czyta ensemble_results.json
    python analyze_ensemble.py --results moj_plik.json # inny plik wyników
    python analyze_ensemble.py --top 5                 # pokaż top-5 (domyślnie 3)
"""

import sys
import json
import argparse
import csv
from pathlib import Path
from datetime import datetime
from loguru import logger

# ─── IMPORT METADANYCH ────────────────────────────────────────────────────────
try:
    from class_meta import CLASS_META, VARIANT_GROUPS, get_meta
except ImportError:
    logger.critical("Brak pliku class_meta.py  –  upewnij się że jest w tym samym folderze.")
    sys.exit(1)

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def avg_variant_acc(result: dict, variant_classes: list[str]) -> float | None:
    """Średnia dokładność ensemble dla klas należących do wariantu."""
    pc = result.get("per_class", {})
    values = [pc[c] for c in variant_classes if c in pc and pc[c] is not None]
    return round(sum(values) / len(values), 2) if values else None


def bar(val: float | None, width: int = 20) -> str:
    if val is None:
        return " " * width
    filled = int(val / 100 * width)
    return "█" * filled + "░" * (width - filled)


def combo_label(combination: list[str]) -> str:
    return " + ".join(combination)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analiza ensemble per wariant choroby")
    parser.add_argument("--results", default="ensemble_results.json",
                        help="Ścieżka do pliku ensemble_results.json")
    parser.add_argument("--top", type=int, default=3,
                        help="Ile top kombinacji pokazać per wariant (domyślnie 3)")
    parser.add_argument("--save-report", action="store_true",
                        help="Zapisz raport TXT i CSV")
    args = parser.parse_args()

    results_path = Path(args.results)
    if not results_path.exists():
        logger.critical(f"Brak pliku: {results_path}")
        logger.info("Uruchom najpierw:  python check_ensemble.py")
        sys.exit(1)

    # ─── Wczytaj JSON ───────────────────────────────────────────────────────
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    all_results: list[dict] = data["all_results"]
    classes: list[str]     = data["classes"]
    generated_at: str      = data.get("generated_at", "?")
    dataset_size: int      = data.get("dataset_size", 0)

    logger.info("=" * 76)
    logger.info(f"  Analiza ensemble per wariant  |  {results_path.name}")
    logger.info(f"  Wygenerowane: {generated_at[:19]}  |  obrazów: {dataset_size}")
    logger.info("=" * 76)

    # ─── 1. SŁOWNIK KLAS ────────────────────────────────────────────────────
    logger.info("\n  KLASY – tłumaczenia i warianty\n")
    logger.info(f"  {'#':>2}  {'EN (folder)':<35} {'PL':<35} {'Wariant':<25} Emoji")
    logger.info(f"  {'-'*2}  {'-'*35} {'-'*35} {'-'*25} {'-'*5}")

    for i, cls in enumerate(classes, 1):
        m = get_meta(cls)
        logger.info(
            f"  {i:>2}  {cls:<35} {m['pl']:<35} {m['variant']:<25} {m['emoji']}"
        )

    # ─── 2. GLOBALNA TABELA WYNIKÓW ─────────────────────────────────────────
    logger.info("\n\n  GLOBALNE WYNIKI – top kombinacje (overall accuracy)\n")
    logger.info(f"  {'#':>3}  {'N':>2}  {'Acc':>7}  Kombinacja")
    logger.info(f"  {'-'*3}  {'-'*2}  {'-'*7}  {'-'*45}")

    for rank, res in enumerate(all_results[:args.top * 3], 1):
        logger.info(
            f"  #{rank:>3}  {res['n_models']:>2}M  {res['accuracy']:>6.2f}%  "
            f"{combo_label(res['combination'])}"
        )

    # ─── 3. ANALIZA PER WARIANT ─────────────────────────────────────────────
    report_lines: list[str] = []
    csv_rows: list[dict]    = []

    for variant, variant_classes in VARIANT_GROUPS.items():
        # Filtruj klasy do tych faktycznie w datasecie
        present = [c for c in variant_classes if c in classes]
        if not present:
            continue

        emoji = CLASS_META[present[0]]["emoji"] if present else "❓"

        logger.info(f"\n{'─'*76}")
        logger.info(f"  {emoji}  WARIANT: {variant}  ({len(present)} klas)")
        logger.info(f"       Klasy: {', '.join(present)}")
        logger.info(f"{'─'*76}")

        # Oblicz avg accuracy per wariant dla każdej kombinacji
        scored: list[tuple[float, dict]] = []
        for res in all_results:
            v_acc = avg_variant_acc(res, present)
            if v_acc is not None:
                scored.append((v_acc, res))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Header
        logger.info(f"  {'#':>3}  {'N':>2}  {'Wariant Acc':>11}  {'Overall':>7}  Kombinacja")
        logger.info(f"  {'-'*3}  {'-'*2}  {'-'*11}  {'-'*7}  {'-'*40}")

        for rank, (v_acc, res) in enumerate(scored[:args.top], 1):
            combo = combo_label(res["combination"])
            tag   = "  ← NAJLEPSZA" if rank == 1 else ""
            logger.info(
                f"  #{rank:>3}  {res['n_models']:>2}M  "
                f"{v_acc:>10.2f}%  {res['accuracy']:>6.2f}%  {combo}{tag}"
            )
            csv_rows.append({
                "variant":        variant,
                "rank":           rank,
                "combination":    combo,
                "n_models":       res["n_models"],
                "variant_acc":    v_acc,
                "overall_acc":    res["accuracy"],
            })

        # Per-klasa dla NAJLEPSZEJ kombinacji w tym wariancie
        if scored:
            best_v_acc, best_res = scored[0]
            pc = best_res.get("per_class", {})
            logger.info(f"\n       Per-klasa dla: {combo_label(best_res['combination'])}")
            for cls in present:
                m      = get_meta(cls)
                v      = pc.get(cls)
                val    = f"{v:.1f}%" if v is not None else "brak"
                b      = bar(v, 22)
                logger.info(f"       {m['emoji']}  {cls:<35} {val:>6}  {b}  [{m['pl']}]")

        report_lines.append(f"\n{'='*76}")
        report_lines.append(f"WARIANT: {variant}")
        report_lines.append(f"Klasy: {', '.join(present)}")
        if scored:
            bv, br = scored[0]
            report_lines.append(f"Najlepsza kombinacja: {combo_label(br['combination'])}  "
                                 f"(variant acc={bv:.2f}%, overall={br['accuracy']:.2f}%)")
            for rank2, (va, rr) in enumerate(scored[:args.top], 1):
                report_lines.append(f"  #{rank2}  {combo_label(rr['combination'])}  "
                                     f"variant={va:.2f}%  overall={rr['accuracy']:.2f}%")

    # ─── 4. PODSUMOWANIE ────────────────────────────────────────────────────
    logger.info(f"\n{'='*76}")
    logger.info("  PODSUMOWANIE – najlepsza kombinacja per wariant\n")
    logger.info(f"  {'Wariant':<28} {'Acc':>7}  Najlepsza kombinacja")
    logger.info(f"  {'-'*28} {'-'*7}  {'-'*40}")

    for variant, variant_classes in VARIANT_GROUPS.items():
        present = [c for c in variant_classes if c in classes]
        if not present:
            continue
        scored = sorted(
            [(avg_variant_acc(r, present), r) for r in all_results
             if avg_variant_acc(r, present) is not None],
            key=lambda x: x[0], reverse=True
        )
        if scored:
            bv, br = scored[0]
            emoji  = CLASS_META[present[0]]["emoji"]
            logger.info(
                f"  {emoji} {variant:<26} {bv:>6.2f}%  "
                f"{combo_label(br['combination'])}"
            )

    logger.info(f"\n  Plik źródłowy : {results_path}")
    logger.info(f"  Kombinacji    : {len(all_results)}")
    logger.info(f"  Klas          : {len(classes)}")
    logger.info(f"  Wariantów     : {len(VARIANT_GROUPS)}")

    # ─── 5. ZAPIS RAPORTU ───────────────────────────────────────────────────
    if args.save_report:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        txt_path = Path(f"variant_report_{ts}.txt")
        txt_path.write_text("\n".join(report_lines), encoding="utf-8")
        logger.success(f"Raport TXT  ->  {txt_path}")

        csv_path = Path(f"variant_report_{ts}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
        logger.success(f"Raport CSV  ->  {csv_path}")

    logger.info(f"\nKoniec: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()