export interface Damage {
  type: string;
  confidence: number;
  location: string;
  bbox?: [number, number, number, number];
}

export interface QualityResult {
  success: boolean;
  message: string;
  sharpness?: number;
  resolution?: { width: number; height: number };
}

export interface DetectionResult {
  hasDamage: boolean;
  damages: Damage[];
  message: string;
  imageWithAnnotations?: string;
  processedImage?: string;
}

export interface InspectionState {
  currentStep: InspectionStep;
  uploadedImage: File | null;
  imagePreview: string;
  qualityResult: QualityResult | null;
  detectionResult: DetectionResult | null;
  isProcessing: boolean;
  error: string | null;
}

export type InspectionStep = 
  | 'upload' 
  | 'quality-check' 
  | 'damage-detection' 
  | 'results';