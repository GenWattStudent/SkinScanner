"""
Central place for all class-level constants.
Mirrors config/settings.py and config/languages.py from the Streamlit prototype —
but without any Streamlit imports so it can be imported anywhere.
"""
from __future__ import annotations

CLASSES: list[str] = [
    "Actinic keratoses",
    "Basal cell carcinoma",
    "Benign keratosis-like lesions",
    "Chickenpox",
    "Cowpox",
    "Dermatofibroma",
    "HFMD",
    "Healthy",
    "Measles",
    "Melanocytic nevi",
    "Melanoma",
    "Monkeypox",
    "Squamous cell carcinoma",
    "Vascular lesions",
]

# risk: 0 = benign (green), 1 = watch (yellow), 2 = see doctor (red)
DISEASE_INFO: dict[str, dict] = {
    "Actinic keratoses": {
        "pl": "Rogowacenie słoneczne",
        "en": "Actinic Keratoses",
        "desc_pl": "Częsta zmiana skórna wywołana słońcem. Może przekształcić się w raka.",
        "desc_en": "Common sun-induced lesion. May develop into skin cancer.",
        "risk": 1,
    },
    "Basal cell carcinoma": {
        "pl": "Rak podstawnokomórkowy",
        "en": "Basal Cell Carcinoma",
        "desc_pl": "Najczęstszy nowotwór złośliwy skóry. Rośnie powoli, rzadko daje przerzuty.",
        "desc_en": "The most common skin cancer. Slow-growing, rarely metastasises.",
        "risk": 2,
    },
    "Benign keratosis-like lesions": {
        "pl": "Łagodne zmiany rogowaciejące",
        "en": "Benign Keratosis",
        "desc_pl": "Zmiany starcze, brodawki łojotokowe. Zazwyczaj niegroźne.",
        "desc_en": "Age spots, seborrhoeic warts. Usually harmless.",
        "risk": 0,
    },
    "Chickenpox": {
        "pl": "Ospa wietrzna",
        "en": "Chickenpox",
        "desc_pl": "Choroba zakaźna (wirusowa).",
        "desc_en": "Highly contagious viral disease.",
        "risk": 1,
    },
    "Cowpox": {
        "pl": "Ospa krowia",
        "en": "Cowpox",
        "desc_pl": "Rzadka choroba wirusowa.",
        "desc_en": "Rare zoonotic viral disease.",
        "risk": 1,
    },
    "Dermatofibroma": {
        "pl": "Włókniak skóry",
        "en": "Dermatofibroma",
        "desc_pl": "Twardy, łagodny guzek pod skórą. Niegroźny.",
        "desc_en": "Hard, benign nodule under the skin. Non-threatening.",
        "risk": 0,
    },
    "Healthy": {
        "pl": "Zdrowa skóra",
        "en": "Healthy Skin",
        "desc_pl": "Nie wykryto niepokojących zmian.",
        "desc_en": "No concerning lesions detected.",
        "risk": 0,
    },
    "HFMD": {
        "pl": "Choroba dłoni, stóp i jamy ustnej",
        "en": "HFMD",
        "desc_pl": "Choroba wirusowa (Bostonka).",
        "desc_en": "Viral disease (Hand, Foot and Mouth Disease).",
        "risk": 1,
    },
    "Measles": {
        "pl": "Odra",
        "en": "Measles",
        "desc_pl": "Wysoce zakaźna choroba wirusowa.",
        "desc_en": "Highly contagious viral disease.",
        "risk": 1,
    },
    "Melanocytic nevi": {
        "pl": "Znamię melanocytowe (Pieprzyk)",
        "en": "Melanocytic Nevi (Mole)",
        "desc_pl": "Typowy pieprzyk. Zazwyczaj łagodny, ale warto obserwować zmiany.",
        "desc_en": "Typical mole. Usually benign; monitor for changes.",
        "risk": 0,
    },
    "Melanoma": {
        "pl": "Czerniak",
        "en": "Melanoma",
        "desc_pl": "Najgroźniejszy nowotwór skóry. Wymaga pilnej wizyty u onkologa!",
        "desc_en": "The most dangerous skin cancer. Requires urgent oncological consultation!",
        "risk": 2,
    },
    "Monkeypox": {
        "pl": "Ospa małpia",
        "en": "Monkeypox",
        "desc_pl": "Choroba wirusowa odzwierzęca.",
        "desc_en": "Zoonotic viral disease.",
        "risk": 1,
    },
    "Squamous cell carcinoma": {
        "pl": "Rak kolczystokomórkowy",
        "en": "Squamous Cell Carcinoma",
        "desc_pl": "Nowotwór złośliwy skóry. Wymaga leczenia.",
        "desc_en": "Malignant skin tumour. Requires medical treatment.",
        "risk": 2,
    },
    "Vascular lesions": {
        "pl": "Zmiany naczyniowe",
        "en": "Vascular Lesions",
        "desc_pl": "Naczyniaki, pajączki. Zazwyczaj łagodne.",
        "desc_en": "Haemangiomas, spider veins. Usually benign.",
        "risk": 0,
    },
}

# Map model_type string → .pth filename
MODEL_FILES: dict[str, str] = {
    "mobilenet": "MobileNetV3_best.pth",
    "resnet50": "ResNet50_best.pth",
    "customcnn": "CustomCNN_best.pth",
    "vit": "ViT_best.pth",
}
