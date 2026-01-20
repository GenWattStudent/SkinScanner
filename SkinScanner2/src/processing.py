import torch
import numpy as np
import cv2
from torchvision import transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from config.settings import DEVICE, CLASSES, IMG_SIZE

# --- Funkcja pomocnicza dla ViT Grad-CAM ---
def reshape_transform_vit(tensor, height=14, width=14):
    # Pomija token klasy (pierwszy) i zmienia kształt na obraz
    result = tensor[:, 1:, :].reshape(tensor.size(0), height, width, tensor.size(2))
    result = result.transpose(2, 3).transpose(1, 2)
    return result
# -------------------------------------------

class ImageProcessor:
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def prepare_image(self, image):
        return self.transform(image).unsqueeze(0).to(DEVICE)

    def predict(self, model, input_tensor):
        with torch.no_grad():
            output = model(input_tensor)
            probs = torch.nn.functional.softmax(output, dim=1)
            top3_prob, top3_idx = torch.topk(probs, 3)
        return top3_prob.cpu().numpy()[0], top3_idx.cpu().numpy()[0]

    def generate_heatmap(self, model, input_tensor, original_image, model_type):
        """Generuje Grad-CAM z inteligentnym wyborem warstwy"""
        try:
            target_layers = None
            reshape_transform = None

            if model_type == 'resnet50':
                target_layers = [model.layer4[-1]]
            
            elif model_type == 'mobilenet':
                target_layers = [model.features[-1]]
                
            elif model_type == 'vit':
                target_layers = [model.encoder.layers[-1].ln_1]
                reshape_transform = reshape_transform_vit
                
            elif model_type == 'customcnn':
                if hasattr(model, 'features'):

                    for layer in reversed(model.features):
                        if isinstance(layer, torch.nn.Conv2d):
                            target_layers = [layer]
                            break

                if target_layers is None:
                    conv_layers = [m for m in model.modules() if isinstance(m, torch.nn.Conv2d)]
                    if conv_layers:
                        target_layers = [conv_layers[-1]]
                # -------------------------------

            if target_layers is None:
                print("Nie znaleziono warstwy docelowej dla Grad-CAM.")
                return cv2.resize(np.array(original_image), (IMG_SIZE, IMG_SIZE))

            # Generowanie CAM
            cam = GradCAM(model=model, target_layers=target_layers, reshape_transform=reshape_transform)
            grayscale_cam = cam(input_tensor=input_tensor, targets=None)[0, :]

            rgb_img = np.float32(original_image) / 255
            rgb_img = cv2.resize(rgb_img, (IMG_SIZE, IMG_SIZE))
            
            return show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

        except Exception as e:
            print(f"Błąd Grad-CAM: {e}")
            # Zwracamy oryginał w razie błędu
            return cv2.resize(np.array(original_image), (IMG_SIZE, IMG_SIZE))