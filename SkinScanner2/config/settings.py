import torch

# Lista klas (zgodna z treningiem)
CLASSES = [
    'Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis-like lesions', 
    'Chickenpox', 'Cowpox', 'Dermatofibroma', 'HFMD', 'Healthy', 'Measles', 
    'Melanocytic nevi', 'Melanoma', 'Monkeypox', 'Squamous cell carcinoma', 
    'Vascular lesions'
]

# Ustawienia
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SHARED_IMAGE_PATH = "shared_buffer/latest_image.jpg"
IMG_SIZE = 224