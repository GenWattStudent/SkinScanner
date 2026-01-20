import os
import streamlit as st
from PIL import Image
from config.settings import SHARED_IMAGE_PATH, CLASSES
import numpy as np 
import time
import hashlib
import io
from config.languages import DISEASE_INFO, UI_TEXT
from src.history_manager import save_to_history, get_history, delete_history_entry, save_images_to_history

class SkinUI:
    def __init__(self, processor, model_handler):
        self.processor = processor
        self.model_handler = model_handler
        if 'lang' not in st.session_state:
            st.session_state['lang'] = 'pl'

    def render_sidebar(self):
        with st.sidebar:
            t = UI_TEXT[st.session_state['lang']]
            st.header(t['title'])

            # Track previous language to detect changes
            prev_lang = st.session_state.get('lang', 'pl')
            lang_choice = st.radio(t['language'], ['Polski', 'English'], horizontal=True, 
                                  index=0 if prev_lang == 'pl' else 1)
            new_lang = 'pl' if lang_choice == 'Polski' else 'en'
            
            # Update language and rerun if changed
            st.session_state['lang'] = new_lang
            if new_lang != prev_lang:
                st.rerun()
            
            st.divider()
            
            # Wybór modelu
            model_name = st.selectbox(t['model_select'], ["MobileNetV3", "ResNet50", "CustomCNN", "ViT"])
            if model_name == "MobileNetV3":
                path = "models/MobileNetV3_best.pth"
                m_type = "mobilenet"
            elif model_name == "ResNet50":
                path = "models/ResNet50_best.pth"
                m_type = "resnet50"
            elif model_name == "CustomCNN":
                path = "models/CustomCNN_best.pth"
                m_type = "customcnn"
            elif model_name == "ViT":
                path = "models/ViT_best.pth"
                m_type = "vit"
            else:
                path = "models/ResNet50_best.pth"
                m_type = "resnet50"
            
            st.divider()
            
            # Wybór trybu pracy (To jest kluczowe dla funkcji Telefon -> PC)
            mode = st.radio(
                t['device_mode'],
                [t['pc_local'], 
                 t['phone_remote'], 
                 t['pc_remote']],
                help=t['device_mode_help']
            )

            st.divider()
            st.subheader(t['crop_image'])
            # 0.0 = brak cięcia, 0.4 = ucięcie 40% brzegów
            crop_factor = st.slider(t['crop_image_slider'], 0.0, 0.5, 0.1, 0.05)
            
            return path, m_type, mode, crop_factor

    def render_results(self, image, model, m_type, crop_factor=0.0):
        """Wyświetla wyniki analizy"""
        print(f"Crop factor: {crop_factor}")
        t = UI_TEXT[st.session_state['lang']]
        lang_code = st.session_state['lang']

        # Store original image before cropping for saving
        original_image = image.copy()

        if crop_factor > 0:
            width, height = image.size
            left = width * crop_factor
            top = height * crop_factor
            right = width * (1 - crop_factor)
            bottom = height * (1 - crop_factor)
            
            # Przycinamy obraz
            image = image.crop((left, top, right, bottom))

        st.divider()
        col1, col2 = st.columns(2)
        
        # 1. Analiza
        with st.spinner(t['analyzing']):
            input_tensor = self.processor.prepare_image(image)
            probs, idxs = self.processor.predict(model, input_tensor)
            
            # GradCAM
            img_np = np.array(image)
            heatmap = self.processor.generate_heatmap(model, input_tensor, img_np, m_type)

        # 2. Wyświetlanie z przyciskami pobierania
        with col1:
            st.image(image, caption=t['input_image'], width='stretch')
            # Download button for input image
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            st.download_button(
                label=t.get('download_image', '📥 Download Image'),
                data=img_bytes,
                file_name=f"skin_scan_{int(time.time())}.png",
                mime="image/png"
            )
        
        with col2:
            st.image(heatmap, caption=t['ai_heatmap'], width='stretch')
            # Download button for heatmap
            # Handle both 0-1 and 0-255 ranges
            if heatmap.max() <= 1.0:
                heatmap_uint8 = (heatmap * 255).astype(np.uint8)
            else:
                heatmap_uint8 = heatmap.astype(np.uint8)
            heatmap_pil = Image.fromarray(heatmap_uint8)
            heatmap_bytes = io.BytesIO()
            heatmap_pil.save(heatmap_bytes, format='PNG')
            heatmap_bytes.seek(0)
            st.download_button(
                label=t.get('download_heatmap', '📥 Download Heatmap'),
                data=heatmap_bytes,
                file_name=f"heatmap_{int(time.time())}.png",
                mime="image/png"
            )

        # --- GŁÓWNA LOGIKA RYZYKA ---
        st.subheader(t['results'])
        
        top_idx = idxs[0]
        top_prob = probs[0]
        top_class_orig = CLASSES[top_idx] # Angielska nazwa z treningu
        
        # Pobieramy info z naszego słownika
        info = DISEASE_INFO.get(top_class_orig, {})
        translated_name = info.get(lang_code, top_class_orig)
        description = info.get('desc_pl' if lang_code == 'pl' else 'en', '')
        risk = info.get('risk', 1)

        # Kolorowanie wyniku
        if risk == 0:
            st.success(f"✅ **{translated_name}**\n\n{t['risk_0']}")
        elif risk == 1:
            st.warning(f"⚠️ **{translated_name}**\n\n{t['risk_1']}")
        else:
            st.error(f"🚨 **{translated_name}**\n\n{t['risk_2']}")
        
        if lang_code == 'pl':
            st.info(f"ℹ️ {description}")

        # Zapisz do historii tylko raz na analizę - używamy hash obrazu
        # Create a hash of the image to track unique analyses
        img_hash = hashlib.md5(np.array(image).tobytes()).hexdigest()
        analysis_key = f"analysis_{img_hash}"
        
        # Only save if this is a new analysis (not just a language change)
        if analysis_key not in st.session_state:
            # Save to history with images
            entry_id = save_to_history(translated_name, top_prob, risk)
            save_images_to_history(entry_id, original_image, heatmap)
            st.session_state[analysis_key] = True
            st.session_state['last_analysis_id'] = entry_id

        # Paski postępu
        st.write("---")
        for i in range(3):
            cls_name = CLASSES[idxs[i]]
            local_name = DISEASE_INFO.get(cls_name, {}).get(lang_code, cls_name)
            p = probs[i]
            st.write(f"{local_name}: **{p*100:.1f}%**")
            st.progress(int(p*100))

    def save_remote_image(self, image_file):
        """Zapisuje zdjęcie wysłane z telefonu do folderu współdzielonego"""
        t = UI_TEXT[st.session_state['lang']]
        folder_path = os.path.dirname(SHARED_IMAGE_PATH)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        img = Image.open(image_file).convert('RGB')
        
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except:
            pass

        img.save(SHARED_IMAGE_PATH)
        st.success(t['image_sent'])
        return img

    def render_history_tab(self):
        lang = st.session_state['lang']
        t = UI_TEXT[lang]
        
        st.header(t['history'])
        
        # Pobieramy oryginalny DataFrame (surowe dane)
        raw_df = get_history()
        
        if raw_df is not None and len(raw_df) > 0:
            # --- PRZYGOTOWANIE DANYCH DO WYŚWIETLENIA (TŁUMACZENIE) ---
            display_df = raw_df.copy()
            
            # 1. Tłumaczenie diagnoz (na podstawie DISEASE_INFO)
            def translate_diagnosis(diag_name):
                info = DISEASE_INFO.get(diag_name)
                if info:
                    return info.get(lang, diag_name)
                return diag_name

            display_df['Diagnoza'] = display_df['Diagnoza'].apply(translate_diagnosis)

            # 2. Tłumaczenie ryzyka (0,1,2 -> Tekst z UI_TEXT)
            def translate_risk_to_text(risk_val):
                key = f"risk_{int(risk_val)}"
                return t.get(key, str(risk_val))
            
            # Zapamiętujemy teksty ryzyka, aby użyć ich w kolorowaniu
            risk_map = {
                0: t.get('risk_0'),
                1: t.get('risk_1'),
                2: t.get('risk_2')
            }
            display_df['Ryzyko'] = display_df['Ryzyko'].apply(translate_risk_to_text)

            # 3. Tłumaczenie nagłówków kolumn
            column_mapping = {
                'Data': t.get('table_date', 'Data'),
                'Diagnoza': t.get('table_diagnosis', 'Diagnoza'),
                'Pewność': t.get('table_confidence', 'Pewność'),
                'Ryzyko': t.get('table_risk', 'Ryzyko')
            }
            display_df = display_df.rename(columns=column_mapping)
            
            # --- STYLOWANIE TABELI ---
            # Funkcja kolorująca musi teraz sprawdzać przetłumaczony tekst
            def highlight_risk_translated(val):
                color = 'white'
                # Porównujemy wartość w komórce z tekstami z tłumaczeń
                if val == risk_map[0]:   color = '#90ee90' # Zielony
                elif val == risk_map[1]: color = '#ffffe0' # Żółty
                elif val == risk_map[2]: color = '#ffcccb' # Czerwony
                return f'background-color: {color}; color: black'

            col_risk_name = t.get('table_risk', 'Ryzyko') # Nazwa kolumny po zmianie
            
            st.dataframe(
                display_df.style.map(highlight_risk_translated, subset=[col_risk_name]),
                use_container_width=True
            )
            
            st.divider()
            
            # --- ZARZĄDZANIE HISTORIĄ (USUWANIE) ---
            st.subheader(t.get('manage_history', 'Manage History'))
            
            # Używamy indeksów z raw_df (który jest odwrócony w get_history)
            entry_ids = raw_df.index.tolist()
            
            if entry_ids:
                # Selectbox pokazuje sformatowany tekst dla użytkownika
                selected_display_id = st.selectbox(
                    t.get('select_entry_to_delete', 'Select entry to delete'),
                    options=entry_ids,
                    format_func=lambda x: f"{display_df.loc[x, column_mapping['Data']]} - {display_df.loc[x, column_mapping['Diagnoza']]}"
                )
                
                col_del, col_view = st.columns([1, 2])
                
                with col_del:
                    st.write("") # Spacer
                    st.write("")
                    if st.button(t.get('delete_entry', '🗑️ Delete Entry'), type="primary", key="del_btn"):
                        # selected_display_id to indeks w tabeli UI (0 = najnowszy)
                        # Funkcja delete_history_entry z Twojego kodu sama przelicza to na indeks w pliku CSV
                        if delete_history_entry(selected_display_id):
                            st.success(t.get('entry_deleted', 'Entry deleted'))
                            st.rerun()
                        else:
                            st.error(t.get('delete_failed', 'Failed to delete'))
                
                with col_view:
                    # Podgląd obrazów
                    # Musimy przeliczyć indeks na rzeczywisty plik (tak jak w delete_history_entry)
                    history_dir = "history_images"
                    total_rows = len(raw_df)
                    actual_index = total_rows - 1 - selected_display_id
                    
                    img_path = os.path.join(history_dir, f"{actual_index}_original.png")
                    heatmap_path = os.path.join(history_dir, f"{actual_index}_heatmap.png")
                    
                    images_found = False
                    if os.path.exists(img_path):
                        images_found = True
                        st.caption(t.get('input_image', 'Original'))
                        st.image(img_path, width=200)
                    
                    if os.path.exists(heatmap_path):
                        images_found = True
                        st.caption(t.get('ai_heatmap', 'Heatmap'))
                        st.image(heatmap_path, width=200)
                        
                    if not images_found:
                        st.info("Brak zapisanych obrazów dla tego wpisu.")

        else:
            st.info(t.get('no_history_entries', 'Brak wpisów w historii.'))