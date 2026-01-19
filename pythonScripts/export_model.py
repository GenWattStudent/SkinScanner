"""
Skrypt do re-eksportu modelu MobileNetV3 z wag .pth do formatu mobile .ptl
WAŻNE: Używa tylko CPU!
"""
import torch
import torch.nn as nn
from torchvision import models
from torch.utils.mobile_optimizer import optimize_for_mobile

device = torch.device('cpu')
print(f"Urządzenie: {device}")

# Liczba klas (14 chorób skóry)
NUM_CLASSES = 14
CLASS_NAMES = [
    'Actinic keratoses',
    'Basal cell carcinoma', 
    'Benign keratosis-like lesions',
    'Chickenpox',
    'Cowpox',
    'Dermatofibroma',
    'HFMD',
    'Healthy',
    'Measles',
    'Melanocytic nevi',
    'Melanoma',
    'Monkeypox',
    'Squamous cell carcinoma',
    'Vascular lesions'
]

print("1. Tworzę architekturę MobileNetV3...")
# Tworzymy model z taką samą architekturą jak podczas treningu
model = models.mobilenet_v3_large(weights=None)  # Bez pretrenowanych wag

# Podmieniamy klasyfikator (tak samo jak w treningu!)
num_ftrs = model.classifier[3].in_features
model.classifier[3] = nn.Linear(num_ftrs, NUM_CLASSES)

print("2. Ładuję wagi z MobileNetV3_best.pth...")
# Załaduj state_dict
state_dict = torch.load('MobileNetV3_best.pth', map_location=device)

# Sprawdź czy to był DataParallel (klucze zaczynają się od "module.")
if any(k.startswith('module.') for k in state_dict.keys()):
    print("   -> Wykryto wagi z DataParallel, usuwam prefiks 'module.'...")
    state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}

model.load_state_dict(state_dict)
model.eval()
model.to(device)
print("   -> Wagi załadowane!")

print("3. Testuję model przed eksportem...")
dummy_input = torch.randn(1, 3, 224, 224).to(device)
with torch.no_grad():
    output = model(dummy_input)
    probs = torch.nn.functional.softmax(output[0], dim=0)
    print(f"   -> Output shape: {output.shape}")
    print(f"   -> Sum of probabilities: {probs.sum().item():.4f}")

print("4. Eksportuję do TorchScript...")
# Użyj scripting zamiast tracing dla lepszej dokładności
scripted_model = torch.jit.script(model)
scripted_model.save('MobileNetV3_scripted.pt')
print("   -> Zapisano: MobileNetV3_scripted.pt")

print("5. Optymalizuję dla mobile...")
optimized_model = optimize_for_mobile(scripted_model)
optimized_model._save_for_lite_interpreter('MobileNetV3_mobile_new.ptl')
print("   -> Zapisano: MobileNetV3_mobile_new.ptl")

print("\n6. Weryfikacja nowego modelu...")
# Załaduj nowy model i przetestuj
new_model = torch.jit.load('MobileNetV3_mobile_new.ptl', map_location=device)
new_model.eval()

with torch.no_grad():
    new_output = new_model(dummy_input)
    new_probs = torch.nn.functional.softmax(new_output[0], dim=0)
    
# Porównaj outputy
diff = torch.abs(output - new_output).max().item()
print(f"   -> Max różnica między oryginałem a eksportem: {diff:.8f}")

if diff < 1e-5:
    print("\n✅ SUKCES! Model wyeksportowany poprawnie!")
    print("   Zastąp stary model nowym:")
    print("   MobileNetV3_mobile_new.ptl -> MobileNetV3_mobile.ptl")
else:
    print("\n⚠️ UWAGA: Wykryto różnice w outputach!")

print("\nGotowe!")
