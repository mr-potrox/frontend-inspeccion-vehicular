from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    # --- Base / API ---
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "vehicular_tfm"
    API_TITLE: str = "TFM Inspector API"
    API_ORIGINS: str = "http://localhost:5173"
    RATE_LIMIT: str = "30/minute"
    LOG_LEVEL: str = "INFO"

    # --- Modelos daños / partes ---
    DAMAGE_MODEL_PATH: str = "models/damage_yolo.pt"
    PARTS_MODEL_PATH: str = "models/parts_yolo.pt"
    DAMAGE_MODEL_NAME: str = "damage-yolo"
    PARTS_MODEL_NAME: str = "parts-yolo"
    DEFAULT_CONF_DAMAGE: float = 0.35
    DEFAULT_CONF_PARTS: float = 0.35
    DAMAGE_LABELS: str = "scratch,dent,broken_glass"
    PART_LABELS: str = "Bonet,Bumper,Door,Headlight,Mirror,Tailight,Windshield"

    MODEL_VERSION: str = "v1.0.0"
    MODEL_SHA: str = "unknown"

    # --- Límites imagen ---
    MAX_IMAGE_MB: int = 8
    MAX_IMAGES_PER_SESSION: int = 30

    # --- Flags PDF / debug ---
    ENABLE_DEBUG_IMAGES: bool = False
    ENABLE_PDF_EXPORT: bool = True

    # --- Preprocesamiento ---
    ENABLE_IMAGE_ENHANCEMENT: bool = True
    ENABLE_DUAL_PASS_DAMAGE: bool = True

    ENABLE_CLASSICAL_SCRATCH: bool = False
    MERGE_IOU_THRESHOLD: float = 0.55

    # --- Segmentación carrocería ---
    ENABLE_SEGMENTATION: bool = True
    SEG_MODEL_PATH: str = "models/vehicle_segment.onnx"
    SEG_MIN_VEHICLE_AREA_RATIO: float = 0.08
    SEG_BOX_MIN_INTERSECTION: float = 0.25
    SEG_USE_MODEL: bool = True
    SEG_THRESHOLD: float = 0.5

    # --- OCR VIN / Placa ---
    ENABLE_OCR: bool = True
    OCR_ENGINE: str = "easyocr"
    OCR_MIN_CONF: float = 0.45
    OCR_VIN_REGEX: str = r"^[A-HJ-NPR-Z0-9]{11,17}$"
    OCR_PLATE_REGEX: str = r"^[A-Z0-9]{5,8}$"
    OCR_MAX_RESULTS: int = 5

    # --- Clasificación fondo ---
    ENABLE_BG_CLASSIFIER: bool = True
    BG_CLASSIFIER_MODEL_PATH: str = "models/bg_classifier.onnx"
    BG_CLASSIFIER_INPUT: int = 224
    BG_LABELS: str = "indoor,outdoor,garage,parking"
    BG_EXPECT_OUTDOOR_KEYS: str = "front,rear"
    BG_OUTDOOR_GROUP: str = "outdoor,parking"
    BG_INDOOR_GROUP: str = "indoor,garage"
    BG_MIN_ACCEPT_SCORE: float = 0.40
    BG_POLICY_EXPECT_OUTDOOR: bool = True

    # --- Iluminación ---
    ENABLE_ILLUMINATION_ANALYSIS: bool = True
    ILLUM_DARK_MEAN: int = 60
    ILLUM_BRIGHT_MEAN: int = 190
    ILLUM_LOW_DR_RANGE: int = 40

    # --- Severidad scratches ---
    ENABLE_SCRATCH_SEVERITY: bool = True
    SCRATCH_SEVERITY_MODEL_PATH: str = "models/scratch_severity.onnx"
    SCRATCH_SEV_LABELS: str = "minor,moderate,severe"
    SCRATCH_SEV_FALLBACK_EDGELEN_MINOR: int = 70
    SCRATCH_SEV_FALLBACK_EDGELEN_SEVERE: int = 220

    # --- Color ---
    ENABLE_COLOR_ANALYSIS: bool = True
    COLOR_KMEANS_K: int = 4
    COLOR_MIN_CLUSTER_RATIO: float = 0.08
    COLOR_DELTAE_THRESHOLD: float = 18.0
    COLOR_FRAUD_RATIO: float = 0.65
    COLOR_REGISTERED_FIELD: str = "color"
    COLOR_FRAUD_POLICY: str = "FLAG"

    # --- Part completeness ---
    ENABLE_PART_COMPLETENESS_SCORE: bool = True

    # --- Tamper ---
    ENABLE_TAMPER_DETECTION: bool = True
    TAMPER_ELA_JPEG_QUALITY: int = 90
    TAMPER_ELA_MEAN_THRESHOLD: float = 18.0
    TAMPER_BLOCK_DIFF_THRESHOLD: float = 28.0
    TAMPER_CNN_MODEL_PATH: str = "models/tamper_forensics.onnx"
    TAMPER_CNN_THRESHOLD: float = 0.55
    TAMPER_EXIF_SOFTWARE_SUSPECT: str = "photoshop,gimp,lightroom"
    TAMPER_EXIF_MISSING_KEYS: str = "Make,Model,DateTimeOriginal"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()