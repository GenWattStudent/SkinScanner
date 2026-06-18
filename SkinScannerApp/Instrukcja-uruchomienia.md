# Instrukcja uruchomienia projektu SkinScannerApp

Niniejsza instrukcja krok po kroku opisuje, jak skonfigurować środowisko i uruchomić część frontendową oraz backendową aplikacji na systemie Windows.

## 1. Wymagania początkowe
Aby w pełni uruchomić projekt na Twoim komputerze, musisz mieć zainstalowane następujące oprogramowanie:

1. **Python** (zalecana wersja z przedziału 3.9 - 3.12). 
   - **Ważne:** Podczas instalacji Pythona na systemie Windows zaznacz opcję **"Add Python to PATH"**.
2. **Node.js** (zalecana wersja LTS, np. 20.x lub nowsza). 
   - Razem z Node.js zostanie zainstalowany menedżer pakietów **npm**, wymaganym do postawienia frontendu.
3. Edytor kodu, np. Visual Studio Code oraz terminal (np. PowerShell lub Git Bash).

---

## 2. Backend (Python + FastAPI)

Backend odpowiedzialny jest m.in. za serwowanie API oraz modele machine learning (PyTorch i sztuczna inteligencja).

### 2.1 Konfiguracja środowiska wirtualnego
1. Otwórz terminal wewnątrz głównego folderu projektu (`SkinScannerApp`).
2. Stwórz prywatne środowisko wirtualne wpisując komendę:
   ```powershell
   python -m venv venv
   ```
3. Aktywuj wirtualne środowisko (na systemie Windows w PowerShell):
   ```powershell
   .\venv\Scripts\activate
   ```
   *(Uwaga: Jeśli pojawi się błąd wykonywania skryptów w PowerShell, uruchom go jako administrator i wpisz: `Set-ExecutionPolicy Unrestricted`)*.   
   Gdy środowisko jest aktywne, z lewej strony terminala zobaczysz przedrostek `(venv)`.

### 2.2 Instalacja zależności backendu
1. Będąc w głównym folderze (ze wciąż aktywnym środowiskiem `(venv)`), przejdź do folderu backend:
   ```powershell
   cd backend
   ```
2. Zainstaluj wszystkie wymagane pakiety bazy danych, frameworka FastAPI i uczenia maszynowego (PyTorch, OpenCV itp):
   ```powershell
   pip install -r requirements.txt
   ```
   *(Zależnie od szybkości łącza może to potrwać parę minut, instalowany jest obszerny pakiet torch).*

### 2.3 Uruchomienie serwera Backendowego
Mając aktywne środowisko i pobrane zainstalowane paczki upewnij się, że jesteś w folderze `backend` i uruchom polecenie:
```powershell
python run.py
```
*(Serwer powinien wystartować bez błędów. W domyślnej konfiguracji dostępny on będzie pod adresami `http://127.0.0.1:8000`)*

---

## 3. Frontend (React + Vite + TypeScript)

Aplikacja kliencka służąca jako interfejs użytkownika do wgrywania/analizowania zdjęć.

### 3.1 Instalacja paczek
1. Otwórz **nowe okno Terminala** (aby zostawić uruchomiony backend w poprzednim).
2. Upewnij się, że jesteś w głównym folderze projektu (SkinScannerApp) i przejdź do katalogu frontendu:
   ```powershell
   cd frontend
   ```
3. Zainstaluj zależności aplikacji wpisując:
   ```powershell
   npm install
   ```

### 3.2 Uruchomienie aplikacji Frontendowej
1. Będąc wciąż w folderze `frontend`, uruchom serwer deweloperski (Vite):
   ```powershell
   npm run dev
   ```
2. Vite automatycznie zbuduje podgląd aplikacji. W terminalu zobaczysz adres logowania dla części frontowej (najczęściej to `http://localhost:5173`). Kliknij go z przyciskiem `Ctrl`, by otworzyć projekt w przeglądarce!

---

## Podsumowanie "Szybkie Uruchamianie" (po wstępnej instalacji wszystkiego):
Gdy już raz zainstalujesz projekt i będziesz chciał go włączyć następnego dnia, wystarczą te szybkie kroki:

**Terminal 1 (Backend):**
```powershell
.\venv\Scripts\activate
cd backend
python run.py
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```