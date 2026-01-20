import torch
import torch.nn as nn
from torchvision import models
from collections import OrderedDict
import streamlit as st
from config.settings import CLASSES, DEVICE
from src.custom_arch import CustomCNN

class ModelHandler:
    def __init__(self):
        self.device = DEVICE

    @st.cache_resource
    def load_model(_self, model_path, model_type):
        """Ładuje model i czyści prefix 'module.'"""
        try:
            # 1. Inicjalizacja architektury
            if model_type == 'resnet50':
                model = models.resnet50(weights=None)
                model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
            elif model_type == 'mobilenet':
                model = models.mobilenet_v3_large(weights=None)
                model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(CLASSES))
            elif model_type == 'customcnn':
                model = CustomCNN(num_classes=len(CLASSES))
            elif model_type == 'vit':
                model = models.vit_b_16(weights=None)
                # W ViT głowica nazywa się 'heads'
                model.heads.head = nn.Linear(model.heads.head.in_features, len(CLASSES))
            else:
                return None

            model.to(_self.device)

            # 2. Ładowanie wag (Fix dla DataParallel)
            state_dict = torch.load(model_path, map_location=torch.device('cpu'))
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                name = k[7:] if k.startswith('module.') else k
                new_state_dict[name] = v
            
            model.load_state_dict(new_state_dict)
            model.eval()
            return model
            
        except Exception as e:
            st.error(f"Błąd modelu: {e}")
            return None