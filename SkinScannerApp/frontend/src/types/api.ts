// ── Prediction / Analysis ────────────────────────────────────────────────────

export interface ClassPrediction {
  class_key: string
  class_pl: string
  class_en: string
  confidence: number
  risk_level: 0 | 1 | 2
  description_pl: string
  description_en: string
}

export interface ModelResult {
  model_type: string
  model_label: string
  primary_prediction: ClassPrediction
  top_predictions: ClassPrediction[]
  heatmap_base64: string
}

export interface AnalyzeResponse {
  scan_id: number
  timestamp: string
  model_results: ModelResult[]
  consensus_class_key: string
  consensus_risk_level: 0 | 1 | 2
  consensus_confidence: number
  original_image_base64: string
}

// ── History ──────────────────────────────────────────────────────────────────

export interface ModelResultEntry {
  model_type: string
  model_label: string
  class_key: string
  class_pl: string
  class_en: string
  confidence: number
  risk_level: 0 | 1 | 2
  top3: { class_key: string; confidence: number; risk_level: number }[] | null
  image_heatmap_url: string | null
}

export interface HistoryEntry {
  id: number
  timestamp: string
  consensus_class_key: string
  consensus_risk_level: 0 | 1 | 2
  consensus_confidence: number
  model_results: ModelResultEntry[]
  image_original_url: string | null
}

export interface HistoryList {
  total: number
  page: number
  limit: number
  items: HistoryEntry[]
}

// ── Health / Models ───────────────────────────────────────────────────────────

export interface ModelInfo {
  model_type: string
  label: string
  available: boolean
}

export interface HealthCheck {
  status: string
  models_loaded: string[]
  device: string
  gpu_name?: string
  gpu_memory_gb?: number
}

export interface ErrorDetail {
  code: string
  message: string
}

// ── App ───────────────────────────────────────────────────────────────────────

export type Language = 'pl' | 'en'
export type ModelType = 'mobilenet' | 'resnet50' | 'customcnn' | 'vit'
export type InputMode = 'upload' | 'camera'
export type Theme = 'system' | 'light' | 'dark'

// ── Body Map ──────────────────────────────────────────────────────────────────

export type BodyMapView = 'front' | 'back'

export interface BodyMapMarker {
  id: number
  created_at: string
  updated_at: string
  x: number
  y: number
  view: BodyMapView
  label: string
  notes: string | null
  scan_id: number | null
  patient_id: number
}

export interface BodyMapMarkerCreate {
  x: number
  y: number
  view: BodyMapView
  label?: string
  notes?: string | null
  scan_id?: number | null
  patient_id: number
}

export interface BodyMapMarkerUpdate {
  x?: number
  y?: number
  view?: BodyMapView
  label?: string
  notes?: string | null
  scan_id?: number | null
}

export interface BodyMapMarkerList {
  total: number
  items: BodyMapMarker[]
}

// ── Patient ───────────────────────────────────────────────────────────────────

export interface Patient {
  id: number
  created_at: string
  updated_at: string
  name: string
  notes: string | null
  marker_count: number
}

export interface PatientCreate {
  name: string
  notes?: string | null
}

export interface PatientUpdate {
  name?: string
  notes?: string | null
}

export interface PatientList {
  total: number
  items: Patient[]
}
