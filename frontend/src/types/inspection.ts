export interface DamageBox {
  label: string
  confidence: number
  box: [number, number, number, number]
}

export interface PartPresence {
  present: boolean
  confidence: number
  box: [number, number, number, number] | null
}

export interface ScratchCandidate {
  box: [number, number, number, number]
  aspect?: number
}
export interface ScratchInfo {
  count: number
  scratch_candidates?: ScratchCandidate[]
}

export interface AnalyzeImageResponse {
  session_id: string
  damage: DamageBox[]
  parts_presence: Record<string, PartPresence>
  missing_parts: string[]
  color_detected: { color_name: string | null; rgb?: [number, number, number] | null }
  vehicle_color_db?: string
  color_match: boolean
  exif_geo: [number, number] | null
  fraud_flags: string[]
  review_flags?: string[]
  aborted: boolean
  abort_reason?: string | null
  images_in_session: number
  preproc_metrics?: {
    lap_var?: number
    edge_density?: number
    mean_gray?: number
    contrast?: number
  }
  scratch?: ScratchInfo
  quality_status?: 'ok' | 'warn' | 'blur' | 'very_blur'
  debug_images?: {
    overlay_b64?: string
    processed_b64?: string
  }
}

export interface FinalizeResponse {
  inspection_id?: string
  session_id: string
  plate?: string
  damage_detections?: DamageBox[]
  parts_presence?: Record<string, PartPresence>
  missing_parts?: string[]
  colors?: { consensus: string | null; all: string[] }
  verdict?: { verdict: string; conditions: string[]; score: number } | null
  vehicle_color_db?: string
  color_match?: boolean
  fraud_flags?: string[]
  review_flags?: string[]
  status: string
  report_markdown?: string
  aborted?: boolean
  abort_reason?: string | null
  vehicle?: any
  driver?: any
  geo?: any
  identity_validated?: boolean
  identity_payload?: any
  vehicle_history?: any
}

export type PhotoKey =
  | 'front'
  | 'rear'
  | 'left'
  | 'right'
  | 'dashboard'
  | 'vin'

export interface QualityThresholds {
  blur_warn: number
  blur_min: number
  blur_very_low: number
}

export interface InspectionState {
  currentStep: string
  sessionId: string
  userInfo?: { name: string; idNumber: string; plate: string }
  geoData?: Partial<Record<PhotoKey, { lat: number; lon: number }>>
  photos: Partial<Record<PhotoKey, File>>
  previews: Partial<Record<PhotoKey, string>>
  analyses: Partial<Record<PhotoKey, AnalyzeImageResponse>>
  aborted: boolean
  abortReason?: string | null
  finalizeResult?: FinalizeResponse | null
  notes: string[]
  error: string | null
  quality?: QualityThresholds
  identity?: { valid: boolean; name: string; document: string } | null
  vehicleHistory?: any
}