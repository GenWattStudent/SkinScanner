# 🩺 SkinScanner

AI-powered skin lesion classification system with a **FastAPI** backend and a **React/TypeScript** frontend. Designed for dermatologists and healthcare professionals to analyze skin lesions using multiple deep-learning models, with Grad-CAM heatmap explanations.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Live Camera – Sender & Viewer](#live-camera--sender--viewer)
6. [AI Models](#ai-models)
7. [Risk Levels](#risk-levels)
8. [Configuration](#configuration)
9. [Ideas & Roadmap for Clinicians](#ideas--roadmap-for-clinicians)
10. [Disclaimer](#disclaimer)

---

## Features

| Feature | Description |
|---|---|
| **Multi-model analysis** | 4 independent AI models (MobileNetV3, ResNet-50, Custom CNN, ViT) – compare results for higher confidence |
| **Grad-CAM heatmaps** | Visual explanation of which image regions influenced the AI's decision |
| **Live Camera streaming** | Stream from phone/dermoscope → computer screen via WebSocket in real time |
| **Risk classification** | 3-tier risk system: Benign / Watch / High Risk |
| **Scan history** | All analyses stored in a local SQLite database with images |
| **Re-analyze** | Same image, different model – no need to re-upload |
| **Crop/Zoom preview** | Adjustable crop factor with live preview before analysis |
| **Light & Dark mode** | System-default theme with manual override |
| **Bilingual UI** | Polish & English (auto-detected from browser) |
| **Mobile-first** | Responsive design with bottom navigation on phones |

---

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   React Frontend    │  HTTP   │   FastAPI Backend     │
│   (Vite + TS)       │◄──────►│   (Python 3.10+)     │
│                     │  WS     │                      │
│  Tailwind + shadcn  │◄──────►│  PyTorch ML models   │
│  TanStack Query     │         │  SQLAlchemy + SQLite │
│  Zustand            │         │  Grad-CAM            │
└─────────────────────┘         └──────────────────────┘
```

---

## Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Model weights** in `models/` directory:
  - `MobileNetV3_best.pth`
  - `ResNet50_best.pth`
  - `CustomCNN_best.pth`
  - `ViT_best.pth`

---

## Quick Start

### 1. Backend

```bash
cd backend

# Create & activate virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the API server
python run.py
# → Server starts at http://localhost:8000
# → All 4 models load at startup (~10-30s depending on hardware)
```

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Development server (hot-reload, proxies API to :8000)
npm run dev
# → Open http://localhost:5173

# OR production build
npm run build
# → Output in frontend/dist/
```

### 3. Both at once

Open two terminals:
- Terminal 1: `cd backend && python run.py`
- Terminal 2: `cd frontend && npm run dev`

Then open **http://localhost:5173** in your browser.

---

## Live Camera – Sender & Viewer

The Live Camera feature enables real-time image streaming from a mobile phone or USB dermoscope to a desktop computer over WebSocket.

### How it works

```
📱 Phone / Dermoscope             🖥️ Desktop / Monitor
┌────────────────────┐            ┌────────────────────┐
│   SENDER mode      │            │   VIEWER mode      │
│                    │            │                    │
│  1. Open /live     │  WebSocket │  1. Open /live     │
│  2. Start camera   │──────────►│  2. Click "Connect │
│  3. Click "Start   │  (JPEG    │     viewer"        │
│     stream"        │  frames)  │  3. See live image │
│                    │            │  4. Capture &      │
│                    │            │     Analyze        │
└────────────────────┘            └────────────────────┘
```

### Setup for doctors

1. **Make sure both devices are on the same network** (Wi-Fi) and the backend is running
2. **On your phone:** Open the SkinScanner website → go to "Live Camera" tab → select "Sender" → allow camera access → tap "Start stream"
3. **On your computer:** Open the SkinScanner website → go to "Live Camera" tab → select "Viewer" → tap "Connect viewer"
4. The live camera feed will appear on your computer screen
5. When you see the lesion clearly, tap **"Capture & Analyze"** to run AI analysis

### Tips
- Use the **rear camera** on the phone for better quality
- If using a **USB dermoscope**, select it from the camera dropdown
- Stream quality is **8 FPS JPEG** – sufficient for clinical review
- Both devices must be able to reach the backend server (same machine or LAN)

---

## AI Models

| Model | Type | Best for | Speed |
|---|---|---|---|
| **MobileNetV3** | Lightweight CNN | Quick screening, mobile use | ⚡ Fastest |
| **ResNet-50** | Deep CNN | General-purpose accuracy | 🔄 Medium |
| **Custom CNN** | Specialized CNN | Dermatology-specific features | 🔄 Medium |
| **Vision Transformer** | Transformer | Complex lesions, global patterns | 🐢 Slowest |

**Recommendation:** Start with MobileNetV3 for quick results, then verify with ResNet-50 or ViT for suspicious lesions. Comparing 2-3 models increases diagnostic confidence.

### Supported conditions (14 classes)

- Actinic keratoses
- Basal cell carcinoma
- Benign keratosis-like lesions
- Chickenpox
- Cowpox
- Dermatofibroma
- Healthy skin
- Hand-foot-mouth disease (HFMD)
- Measles
- Melanocytic nevi (moles)
- Melanoma
- Monkeypox
- Squamous cell carcinoma
- Vascular lesions

---

## Risk Levels

| Level | Label | Color | Meaning |
|---|---|---|---|
| 0 | **Benign** | 🟢 Green | Low risk – routine follow-up |
| 1 | **Watch** | 🟡 Amber | Medium risk – monitor and consider referral |
| 2 | **High Risk** | 🔴 Red | Urgent – refer to dermatologist/oncologist |

---

## Configuration

### Backend (.env file in `backend/`)

```env
MODELS_DIR=../models        # Path to .pth weight files
DB_URL=sqlite:///./skinscanner.db
HISTORY_IMAGES_DIR=./history_images
CORS_ORIGINS=["*"]
LOG_LEVEL=INFO
```

### Frontend (Settings panel ⚙️)

- **Theme:** System / Light / Dark
- **Language:** Auto-detected (Polish/English), manually switchable
- **AI Model:** Select which model to use for analysis
- **Crop/Zoom:** 0–50% symmetric edge crop

---

## Ideas & Roadmap for Clinicians

These features could further enhance SkinScanner for clinical use:

### 📊 Patient Management
- **Patient profiles** – link scan history to individual patients
- **PDF report export** – generate printable reports with images, heatmaps, and AI assessment for patient records
- **DICOM integration** – import/export dermoscopy images in medical standard format

### 🔄 Comparison Tools
- **Side-by-side comparison** – compare the same lesion across multiple visits to track evolution
- **Multi-model consensus** – automatically run all 4 models and show agreement/disagreement
- **Lesion body map** – mark lesion locations on a body diagram for spatial tracking

### 📱 Mobile & Dermoscope
- **Offline mode** – cache the AI model on device for use without internet
- **Dermoscope calibration** – color/white balance calibration for consistent imaging
- **Measurement overlay** – ruler/scale on captured images for lesion size tracking

### 🔬 Clinical Workflow
- **ABCDE checklist integration** – overlay Asymmetry, Border, Color, Diameter, Evolution scoring
- **Referral workflow** – one-click generate referral letter with AI findings
- **Annotation tools** – draw on images to highlight areas of concern
- **Second opinion sharing** – securely share cases with colleagues for consultation

### 🛡️ Safety & Compliance
- **Audit trail** – log all analyses with timestamps for medical records
- **Confidence thresholds** – configurable minimum confidence before showing results
- **HIPAA/GDPR data handling** – encrypted storage, patient data anonymization

---

## Disclaimer

⚠️ **SkinScanner is an assistive research tool and does NOT constitute a medical diagnosis.**

Results are generated by AI models trained on public dermatological datasets and should **always be verified by a qualified dermatologist**. The system is intended to support — not replace — clinical decision-making.

In case of any doubt about a skin lesion, **always consult a medical professional.**

---

## License

This project is part of academic research at the university. All rights reserved.
