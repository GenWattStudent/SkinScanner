"""
Skrypt do testowania modelu MobileNetV3 na CPU
Model wytrenowany do klasyfikacji chorób skóry (14 klas)
"""
import torch
from PIL import Image
import torchvision.transforms as transforms
import sys
import os

# ==========================================
# KONFIGURACJA - TYLKO CPU!
# ==========================================
# Wymuszamy użycie CPU (ważne dla mobilki!)
device = torch.device('cpu')
print(f"Używane urządzenie: {device}")

# Klasy z treningu (14 klas chorób skóry)
CLASS_NAMES = [
    'Actinic keratoses',           # 0 - Rogowacenie słoneczne
    'Basal cell carcinoma',        # 1 - Rak podstawnokomórkowy
    'Benign keratosis-like lesions', # 2 - Łagodne zmiany rogowaciejące
    'Chickenpox',                  # 3 - Ospa wietrzna
    'Cowpox',                      # 4 - Ospa krowia
    'Dermatofibroma',              # 5 - Włókniak skórny
    'HFMD',                        # 6 - Choroba rąk, stóp i ust
    'Healthy',                     # 7 - Zdrowa skóra
    'Measles',                     # 8 - Odra
    'Melanocytic nevi',            # 9 - Znamiona melanocytowe
    'Melanoma',                    # 10 - Czerniak
    'Monkeypox',                   # 11 - Małpia ospa
    'Squamous cell carcinoma',     # 12 - Rak płaskonabłonkowy
    'Vascular lesions'             # 13 - Zmiany naczyniowe
]

# Transformacje obrazu (takie same jak podczas treningu!)
IMG_SIZE = 224
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def load_model(model_path: str):
    """
    Ładuje model TorchScript (.ptl lub .pt) na CPU
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Nie znaleziono modelu: {model_path}")
    
    print(f"Ładowanie modelu z: {model_path}")
    
    # Ładujemy model TorchScript (wersja mobile .ptl)
    model = torch.jit.load(model_path, map_location=device)
    model.eval()  # Tryb ewaluacji (bez dropoutu itp.)
    model.to(device)
    
    print("Model załadowany pomyślnie na CPU!")
    return model


def preprocess_image(image_path: str):
    """
    Wczytuje i przetwarza obraz do formatu wymaganego przez model
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Nie znaleziono obrazu: {image_path}")
    
    # Wczytaj obraz i konwertuj do RGB (na wypadek PNG z alfą)
    image = Image.open(image_path).convert('RGB')
    
    # Zastosuj transformacje
    input_tensor = transform(image)
    
    # Dodaj wymiar batch (model oczekuje [batch, channels, height, width])
    input_batch = input_tensor.unsqueeze(0)
    
    return input_batch.to(device)


def predict(model, image_tensor):
    """
    Wykonuje predykcję na obrazie
    Zwraca: (predicted_class_name, confidence, all_probabilities)
    """
    with torch.no_grad():  # Wyłączamy gradient (nie trenujemy!)
        outputs = model(image_tensor)
        
        # Softmax dla prawdopodobieństw
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        # Znajdź klasę z najwyższym prawdopodobieństwem
        confidence, predicted_idx = torch.max(probabilities, 0)
        
        predicted_class = CLASS_NAMES[predicted_idx.item()]
        confidence_value = confidence.item() * 100  # W procentach
        
        return predicted_class, confidence_value, probabilities


def main():
    # Ścieżka do modelu
    model_path = os.path.join(os.path.dirname(__file__), 'MobileNetV3_mobile.ptl')
    
    # Sprawdź czy podano ścieżkę do obrazu
    if len(sys.argv) < 2:
        print("\nUżycie: python run_model.py <ścieżka_do_obrazu>")
        print("Przykład: python run_model.py test_image.jpg")
        
        # Tryb demo - sprawdź czy model się ładuje
        print("\n--- TRYB DEMO (bez obrazu) ---")
        model = load_model(model_path)
        
        # Test z losowym tensorem
        print("\nTest z losowym tensorem (224x224)...")
        dummy_input = torch.randn(1, 3, 224, 224).to(device)
        with torch.no_grad():
            output = model(dummy_input)
        print(f"Output shape: {output.shape}")
        print(f"Model działa poprawnie na CPU!")
        return
    
    image_path = sys.argv[1]
    
    # Załaduj model
    model = load_model(model_path)
    
    # Przetwórz obraz
    print(f"\nPrzetwarzanie obrazu: {image_path}")
    image_tensor = preprocess_image(image_path)
    
    # Wykonaj predykcję
    predicted_class, confidence, probabilities = predict(model, image_tensor)
    
    # Wyświetl wyniki
    print("\n" + "="*50)
    print("WYNIK PREDYKCJI")
    print("="*50)
    print(f"Przewidywana klasa: {predicted_class}")
    print(f"Pewność: {confidence:.2f}%")
    print("\nTop 5 predykcji:")
    print("-"*50)
    
    # Sortuj i wyświetl top 5
    probs_with_names = [(CLASS_NAMES[i], probabilities[i].item() * 100) 
                        for i in range(len(CLASS_NAMES))]
    probs_with_names.sort(key=lambda x: x[1], reverse=True)
    
    for i, (name, prob) in enumerate(probs_with_names[:5], 1):
        print(f"{i}. {name}: {prob:.2f}%")


if __name__ == "__main__":
    main()