"""
class_meta.py  –  Metadane klas (tłumaczenia PL/EN + kategoria choroby)
========================================================================
Importuj ten moduł w dowolnym skrypcie:

    from class_meta import CLASS_META, get_meta, VARIANT_GROUPS

Struktura CLASS_META:
    {
        "Actinic keratoses": {
            "pl":       "Rogowacenie słoneczne",
            "en":       "Actinic Keratoses",
            "variant":  "Przednowotworowe",
            "variant_en": "Pre-cancerous",
            "emoji":    "☀️",
            "desc_pl":  "Krótki opis po polsku",
            "desc_en":  "Short description in English",
        },
        ...
    }
"""

CLASS_META: dict[str, dict] = {
    "Actinic keratoses": {
        "pl":         "Rogowacenie słoneczne",
        "en":         "Actinic Keratoses",
        "variant":    "Przednowotworowe",
        "variant_en": "Pre-cancerous",
        "emoji":      "☀️",
        "desc_pl":    "Zmiany skórne wywołane długotrwałym działaniem UV, mogą przekształcić się w raka.",
        "desc_en":    "Rough, scaly skin patches caused by UV damage; may progress to squamous cell carcinoma.",
    },
    "Basal cell carcinoma": {
        "pl":         "Rak podstawnokomórkowy",
        "en":         "Basal Cell Carcinoma",
        "variant":    "Nowotworowe (rak skóry)",
        "variant_en": "Cancerous (skin cancer)",
        "emoji":      "🔴",
        "desc_pl":    "Najczęstszy nowotwór złośliwy skóry, rzadko daje przerzuty, lecz wymaga usunięcia.",
        "desc_en":    "Most common skin cancer; rarely metastasizes but requires surgical removal.",
    },
    "Benign keratosis-like lesions": {
        "pl":         "Łagodne zmiany rogowaciejące",
        "en":         "Benign Keratosis-like Lesions",
        "variant":    "Łagodne",
        "variant_en": "Benign",
        "emoji":      "🟡",
        "desc_pl":    "Nieinwazyjne zmiany skórne m.in. rogowacenie łojotokowe; nie są złośliwe.",
        "desc_en":    "Non-invasive lesions (e.g. seborrheic keratosis); benign, no malignant potential.",
    },
    "Chickenpox": {
        "pl":         "Ospa wietrzna",
        "en":         "Chickenpox (Varicella)",
        "variant":    "Wirusowe",
        "variant_en": "Viral",
        "emoji":      "🦠",
        "desc_pl":    "Wysoce zaraźliwa choroba wirusowa (VZV) objawiająca się swędzącą wysypką pęcherzykową.",
        "desc_en":    "Highly contagious VZV infection; itchy blister-like rash, mainly affects children.",
    },
    "Cowpox": {
        "pl":         "Ospa krowianka",
        "en":         "Cowpox",
        "variant":    "Wirusowe",
        "variant_en": "Viral",
        "emoji":      "🦠",
        "desc_pl":    "Rzadka infekcja wirusowa (Orthopoxvirus) przenoszona ze zwierząt; lokalne zmiany skórne.",
        "desc_en":    "Rare zoonotic Orthopoxvirus infection; causes localized pustular skin lesions.",
    },
    "Dermatofibroma": {
        "pl":         "Włókniak skóry",
        "en":         "Dermatofibroma",
        "variant":    "Łagodne",
        "variant_en": "Benign",
        "emoji":      "🟡",
        "desc_pl":    "Łagodny guzek skórny zbudowany z fibroblastów; zwykle niegroźny, może być usunięty.",
        "desc_en":    "Benign fibrous skin nodule; harmless, can be excised if bothersome.",
    },
    "Healthy": {
        "pl":         "Zdrowa skóra",
        "en":         "Healthy Skin",
        "variant":    "Zdrowe",
        "variant_en": "Healthy",
        "emoji":      "✅",
        "desc_pl":    "Skóra bez widocznych zmian chorobowych.",
        "desc_en":    "Skin with no visible pathological changes.",
    },
    "HFMD": {
        "pl":         "Choroba rąk, stóp i ust",
        "en":         "Hand, Foot and Mouth Disease (HFMD)",
        "variant":    "Wirusowe",
        "variant_en": "Viral",
        "emoji":      "🦠",
        "desc_pl":    "Wirusowa choroba dziecięca (Enterowirus); wysypka na dłoniach, stopach i w jamie ustnej.",
        "desc_en":    "Contagious Enterovirus illness in children; rash on hands, feet and mouth.",
    },
    "Measles": {
        "pl":         "Odra",
        "en":         "Measles (Rubeola)",
        "variant":    "Wirusowe",
        "variant_en": "Viral",
        "emoji":      "🦠",
        "desc_pl":    "Wysoce zaraźliwa choroba wirusowa; wysypka grudkowa, gorączka, kaszel.",
        "desc_en":    "Highly contagious Paramyxovirus; maculopapular rash, fever, cough.",
    },
    "Melanocytic nevi": {
        "pl":         "Znamię melanocytarne (pieprzyk)",
        "en":         "Melanocytic Nevi (Mole)",
        "variant":    "Łagodne",
        "variant_en": "Benign",
        "emoji":      "🟤",
        "desc_pl":    "Łagodne skupisko melanocytów – zwykły pieprzyk. Wymaga obserwacji metodą ABCDE.",
        "desc_en":    "Benign cluster of melanocytes (common mole). Monitor with ABCDE rule.",
    },
    "Melanoma": {
        "pl":         "Czerniak złośliwy",
        "en":         "Melanoma",
        "variant":    "Nowotworowe (rak skóry)",
        "variant_en": "Cancerous (skin cancer)",
        "emoji":      "🔴",
        "desc_pl":    "Najgroźniejszy nowotwór skóry wywodzący się z melanocytów; szybko daje przerzuty.",
        "desc_en":    "Most dangerous skin cancer; arises from melanocytes, metastasizes rapidly.",
    },
    "Monkeypox": {
        "pl":         "Małpie ospa (mpox)",
        "en":         "Monkeypox (Mpox)",
        "variant":    "Wirusowe",
        "variant_en": "Viral",
        "emoji":      "🦠",
        "desc_pl":    "Wirusowa choroba odzwierzęca (Orthopoxvirus); pęcherzowo-krostkowa wysypka, gorączka.",
        "desc_en":    "Zoonotic Orthopoxvirus; vesicular/pustular rash, fever, lymphadenopathy.",
    },
    "Squamous cell carcinoma": {
        "pl":         "Rak płaskonabłonkowy",
        "en":         "Squamous Cell Carcinoma",
        "variant":    "Nowotworowe (rak skóry)",
        "variant_en": "Cancerous (skin cancer)",
        "emoji":      "🔴",
        "desc_pl":    "Złośliwy nowotwór naskórka wywodzący się z keratynocytów; może dawać przerzuty.",
        "desc_en":    "Malignant keratinocyte cancer; can metastasize if left untreated.",
    },
    "Vascular lesions": {
        "pl":         "Zmiany naczyniowe",
        "en":         "Vascular Lesions",
        "variant":    "Naczyniowe / Łagodne",
        "variant_en": "Vascular / Benign",
        "emoji":      "💜",
        "desc_pl":    "Zmiany wynikające z nieprawidłowości naczyń krwionośnych (naczyniaki, teleangiektazje itp.).",
        "desc_en":    "Skin changes from abnormal blood vessels (hemangiomas, telangiectasias, etc.).",
    },
}

# ─── Grupy wariantów  (do analizy per-variant w analyze_ensemble.py) ──────────

VARIANT_GROUPS: dict[str, list[str]] = {}
for cls, meta in CLASS_META.items():
    v = meta["variant"]
    VARIANT_GROUPS.setdefault(v, []).append(cls)


def get_meta(class_name: str) -> dict:
    """Zwraca metadane dla klasy lub pusty słownik jeśli klasa nieznana."""
    return CLASS_META.get(class_name, {
        "pl": class_name, "en": class_name,
        "variant": "Nieznane", "variant_en": "Unknown",
        "emoji": "❓", "desc_pl": "", "desc_en": "",
    })


if __name__ == "__main__":
    print(f"{'Klasa EN':<35} {'PL':<35} {'Wariant'}")
    print("-" * 90)
    for cls, m in CLASS_META.items():
        print(f"{cls:<35} {m['pl']:<35} {m['emoji']} {m['variant']}")

    print(f"\nGrupy wariantów ({len(VARIANT_GROUPS)}):")
    for variant, classes in VARIANT_GROUPS.items():
        print(f"  {variant}: {', '.join(classes)}")