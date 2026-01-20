import torch
import torch.nn as nn
from torchvision import models
from config.settings import IMG_SIZE, DEVICE

# 1. Prosty Custom CNN (jako baseline)
class CustomCNN(nn.Module):
    def __init__(self, num_classes):
        super(CustomCNN, self).__init__()
        self.features = nn.Sequential(
            # Wejście: 3 kanały (RGB), Wyjście: 32
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # POPRAWKA TUTAJ: Wejście 32 (z poprzedniej warstwy), Wyjście 64
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            
            # Wejście 64, Wyjście 128
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            # Obraz 224x224 po 3 poolingach (dzielenie przez 2 trzykrotnie) = 28x28
            # 224 / 2 / 2 / 2 = 28. Stąd wymiar: 128 kanałów * 28 * 28
            nn.Linear(128 * (IMG_SIZE // 8) * (IMG_SIZE // 8), 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Funkcja budująca modele
def get_model(model_name, num_classes, pretrained=True):
    print(f"Initializing {model_name}...")
    
    if model_name == 'CustomCNN':
        model = CustomCNN(num_classes)
        
    elif model_name == 'ResNet50':
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
        # Podmiana ostatniej warstwy (fc)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
        
    elif model_name == 'MobileNetV3':
        weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_large(weights=weights)
        # Podmiana klasyfikatora
        num_ftrs = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(num_ftrs, num_classes)
        
    elif model_name == 'ViT':
        # Vision Transformer Base 16
        weights = models.ViT_B_16_Weights.DEFAULT if pretrained else None
        model = models.vit_b_16(weights=weights)
        # Podmiana głowicy (heads)
        num_ftrs = model.heads.head.in_features
        model.heads.head = nn.Linear(num_ftrs, num_classes)
        
    else:
        raise ValueError("Unknown model name")

    # Obsługa wielu GPU
    if torch.cuda.device_count() > 1:
        # print(f"Używam {torch.cuda.device_count()} GPU dla modelu {model_name}")
        model = nn.DataParallel(model)
        
    return model.to(DEVICE)