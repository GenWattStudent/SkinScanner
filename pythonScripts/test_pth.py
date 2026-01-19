"""
Test bezpośrednio na modelu z wagami .pth (bez eksportu do .ptl)
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import sys

device = torch.device('cpu')
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

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

print("Ładuję model bezpośrednio z .pth...")
model = models.mobilenet_v3_large(weights=None)
num_ftrs = model.classifier[3].in_features
model.classifier[3] = nn.Linear(num_ftrs, NUM_CLASSES)

state_dict = torch.load('MobileNetV3_best.pth', map_location=device)
if any(k.startswith('module.') for k in state_dict.keys()):
    state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}
model.load_state_dict(state_dict)
model.eval()
model.to(device)

# Test na obrazku
image_path = sys.argv[1] if len(sys.argv) > 1 else 'HFMD_106_01_1.jpg'
print(f"\nTestuję na: {image_path}")

image = Image.open(image_path).convert('RGB')
input_tensor = transform(image).unsqueeze(0).to(device)

with torch.no_grad():
    output = model(input_tensor)
    probs = torch.nn.functional.softmax(output[0], dim=0)

print("\n" + "="*50)
print("WYNIK (bezpośrednio z .pth)")
print("="*50)

results = [(CLASS_NAMES[i], probs[i].item() * 100) for i in range(NUM_CLASSES)]
results.sort(key=lambda x: x[1], reverse=True)

for i, (name, prob) in enumerate(results[:5], 1):
    print(f"{i}. {name}: {prob:.2f}%")
