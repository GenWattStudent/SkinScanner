# src/history_manager.py
import pandas as pd
import os
import numpy as np
from datetime import datetime
from PIL import Image

HISTORY_FILE = "history.csv"
HISTORY_IMAGES_DIR = "history_images"

def save_to_history(predicted_class, confidence, risk_level):
    """Zapisuje wynik badania do CSV i zwraca ID wpisu (actual index in file)"""
    
    # Przygotuj dane
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        'Data': [timestamp],
        'Diagnoza': [predicted_class],
        'Pewność': [f"{confidence*100:.1f}%"],
        'Ryzyko': [risk_level] # 0, 1, 2
    }
    df_new = pd.DataFrame(data)
    
    # Dopisz do pliku (lub stwórz nowy)
    if not os.path.exists(HISTORY_FILE):
        df_new.to_csv(HISTORY_FILE, index=False)
        # Return index 0 for the first entry (actual index in file)
        return 0
    else:
        # Read existing file to get the next index
        df_existing = pd.read_csv(HISTORY_FILE)
        next_id = len(df_existing)
        df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)
        # Return actual index in file (will be shown as reversed in UI)
        return next_id

def get_history():
    """Wczytuje historię"""
    if os.path.exists(HISTORY_FILE):
        # Wczytujemy od najnowszych
        df = pd.read_csv(HISTORY_FILE)
        # Reset index to use as entry ID
        df = df.reset_index()
        return df.iloc[::-1].reset_index(drop=True)
    return None

def delete_history_entry(entry_id):
    """Usuwa wpis z historii na podstawie ID (entry_id jest z reversed dataframe)"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return False
        
        df = pd.read_csv(HISTORY_FILE)
        total_rows = len(df)
        
        # entry_id is from reversed dataframe, so we need to convert it
        # If we have 10 rows (0-9), and entry_id is 0 (newest), actual index is 9
        actual_index = total_rows - 1 - entry_id
        
        if actual_index < 0 or actual_index >= total_rows:
            return False
        
        # Delete the row by actual index
        df = df.drop(df.index[actual_index]).reset_index(drop=True)
        df.to_csv(HISTORY_FILE, index=False)
        
        # Also delete associated images (use actual_index for file naming)
        img_path = os.path.join(HISTORY_IMAGES_DIR, f"{actual_index}_original.png")
        heatmap_path = os.path.join(HISTORY_IMAGES_DIR, f"{actual_index}_heatmap.png")
        
        if os.path.exists(img_path):
            os.remove(img_path)
        if os.path.exists(heatmap_path):
            os.remove(heatmap_path)
        
        return True
    except Exception as e:
        print(f"Error deleting history entry: {e}")
        return False

def save_images_to_history(entry_id, original_image, heatmap):
    """Zapisuje obrazy do historii"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(HISTORY_IMAGES_DIR, exist_ok=True)
        
        # Save original image
        img_path = os.path.join(HISTORY_IMAGES_DIR, f"{entry_id}_original.png")
        if isinstance(original_image, Image.Image):
            original_image.save(img_path)
        else:
            Image.fromarray(original_image).save(img_path)
        
        # Save heatmap
        heatmap_path = os.path.join(HISTORY_IMAGES_DIR, f"{entry_id}_heatmap.png")
        if isinstance(heatmap, np.ndarray):
            # Convert to PIL Image if needed
            if heatmap.max() <= 1.0:
                heatmap_uint8 = (heatmap * 255).astype(np.uint8)
            else:
                heatmap_uint8 = heatmap.astype(np.uint8)
            Image.fromarray(heatmap_uint8).save(heatmap_path)
        else:
            heatmap.save(heatmap_path)
        
        return True
    except Exception as e:
        print(f"Error saving images to history: {e}")
        return False