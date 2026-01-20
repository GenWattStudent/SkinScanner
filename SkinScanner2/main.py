import streamlit as st
import os
import time
from PIL import Image
from config.languages import UI_TEXT
from src.model_loader import ModelHandler
from src.processing import ImageProcessor
from ui.interface import SkinUI
from config.settings import SHARED_IMAGE_PATH

# Ustawienia strony
st.set_page_config(page_title="SkinScanner Pro", layout="wide", page_icon="🩺")

def main():
    if 'lang' not in st.session_state:
        st.session_state['lang'] = 'pl'

    t = UI_TEXT[st.session_state['lang']]
    st.title(t['title'])

    # Inicjalizacja klas
    loader = ModelHandler()
    processor = ImageProcessor()
    ui = SkinUI(processor, loader)

    # 1. Pobierz konfigurację z Paska Bocznego
    model_path, model_type, mode, crop_factor = ui.render_sidebar()

    # 2. Załaduj model
    tab1, tab2 = st.tabs(["🔍 " + t['analyze'], "📜 " + t['history']])

    # --- ZAKŁADKA 1: SKANER ---
    with tab1:
        model = loader.load_model(model_path, model_type)
        if not model:
            st.stop()
        
        if mode == t['pc_local']:
            uploaded_file = st.file_uploader(t['upload'], type=['jpg', 'png'])
            if uploaded_file:
                image = Image.open(uploaded_file).convert('RGB')
                ui.render_results(image, model, model_type, crop_factor)

        elif mode == t['phone_remote']:
            st.info(t['phone_remote_info'])
            camera_file = st.camera_input(t['camera'])
            
            if camera_file:
                ui.save_remote_image(camera_file)

        elif mode == t['pc_remote']:
            st.info(t['pc_remote_info'])
            placeholder = st.empty()
            if st.button(t['refresh_manually']):
                st.rerun()

            # Sprawdź czy plik istnieje
            if os.path.exists(SHARED_IMAGE_PATH):
                # Pobierz czas modyfikacji, żeby wyświetlić użytkownikowi
                last_mod_time = os.path.getmtime(SHARED_IMAGE_PATH)
                
                with placeholder.container():
                    st.success(f"{t['image_received']} {t['time']}: {time.ctime(last_mod_time)}")
                    
                    success = False
                    last_error = ""
                    for attempt in range(5):
                        try:
                            image = Image.open(SHARED_IMAGE_PATH).convert('RGB')
                            image.load()
                            ui.render_results(image, model, model_type, crop_factor)
                            success = True
                            break 
                        except Exception as e:
                            # Jeśli błąd (np. plik zajęty), czekamy i próbujemy dalej
                            last_error = str(e)
                            time.sleep(0.5)
                    
                    if not success:
                        st.error(f"{t['file_not_loaded']} {last_error}")
                        st.warning(t['try_again'])
                    # -----------------------------------

            else:
                placeholder.warning(t['no_image_in_buffer'])

            # Automatyczne odświeżanie co 3 sekundy
            time.sleep(3)
            st.rerun()
    with tab2:
        ui.render_history_tab()
        
if __name__ == "__main__":
    main()