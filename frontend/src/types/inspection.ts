export interface Damage {
  type: string
  confidence: number
  location: string
  bbox?: [number, number, number, number]
}

export interface QualityResult {
  success: boolean
  message: string
  sharpness?: number
  resolution?: { width: number; height: number }
}

export interface DetectionResult {
  hasDamage: boolean
  damages: Damage[]
  message: string
  imageWithAnnotations?: string
  processedImage?: string
}

export type PhotoKey =
  | 'front'
  | 'rear'
  | 'left'
  | 'right'
  | 'dashboard'
  | 'vin'

export type PhotoRequirement = {
  key: PhotoKey
  label: string
  helper: string
}

export type InspectionStep =
  | 'user-info'
  | 'upload-image'
  | 'landing'
  | PhotoKey
  | 'quality-check'
  | 'damage-detection'
  | 'results'

export interface InspectionState {
  currentStep: InspectionStep
  userInfo?: {
    name: string
    idNumber: string
    plate: string
  }
  geoData?: Partial<Record<PhotoKey, { lat: number; lon: number }>>
  photos: Partial<Record<PhotoKey, File>>
  previews: Partial<Record<PhotoKey, string>>
  qualityResult: QualityResult | null
  detectionResult: DetectionResult | null
  isProcessing: boolean
  notes: string[]
  error: string | null
}