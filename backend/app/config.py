from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    # ---------------- Infra / DB ----------------
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "vehicular_tfm"

    # ---------------- API Meta -----------------
    API_TITLE: str = "TFM Inspector API"
    API_ORIGINS: str = "http://localhost:5173"

    # ---------------- Modelos YOLO (2 modelos) -------------
    DAMAGE_MODEL_PATH: str = "models/damage_yolo.pt"
    PARTS_MODEL_PATH: str = "models/parts_yolo.pt"
    DAMAGE_MODEL_NAME: str = "damage-yolo"
    PARTS_MODEL_NAME: str = "parts-yolo"
    DEFAULT_CONF_DAMAGE: float = 0.35
    DEFAULT_CONF_PARTS: float = 0.35

    # ---------------- Listas de clases (de data.yaml reales) -----------
    # dataset_maestro_danos/data.yaml -> scratch, dent, broken_glass
    DAMAGE_LABELS: str = "scratch,dent,broken_glass"
    # dataset_maestro_partes/data.yaml -> ['Bonet','Bumper','Door','Headlight','Mirror','Tailight','Windshield']
    PART_LABELS: str = "Bonet,Bumper,Door,Headlight,Mirror,Tailight,Windshield"

    # ---------------- Calidad / límites / sesión ----------------
    MODEL_VERSION: str = "v1.0.0"
    MODEL_SHA: str = "unknown"
    MAX_IMAGE_MB: int = 8
    MAX_IMAGES_PER_SESSION: int = 30
    RATE_LIMIT: str = "30/minute"
    LOG_LEVEL: str = "INFO"

    # ---------------- Flags PDF / Debug ----------------
    ENABLE_DEBUG_IMAGES: bool = False
    ENABLE_PDF_EXPORT: bool = True
    PDF_TITLE: str = "Reporte Inspección Vehicular"
    PDF_AUTHOR: str = "Sistema Inspección"
    PDF_INCLUDE_IMAGES: bool = True
    PDF_MAX_IMAGE_WIDTH: int = 520

    # ---------------- Geolocalización / Políticas ----------------
    COLOR_MISMATCH_POLICY: str = "REVIEW"   # REVIEW | ABORT | FLAG
    GEO_WARN_DISTANCE: float = 300.0
    GEO_HARD_DISTANCE: float = 1000.0
    GEO_ABORT_AFTER_WARN: int = 2

    # ---------------- Preprocesamiento / Clásicos ----------------
    ENABLE_IMAGE_ENHANCEMENT: bool = True
    ENABLE_DUAL_PASS_DAMAGE: bool = True
    ENABLE_CLASSICAL_SCRATCH: bool = True
    CLASSICAL_SCRATCH_MAX: int = 8
    CLASSICAL_SCRATCH_MIN_LEN: int = 24
    CLASSICAL_SCRATCH_MAX_WIDTH: int = 18
    MERGE_IOU_THRESHOLD: float = 0.55
    CLASSICAL_FAKE_CONF: float = 0.32
    ENHANCEMENT_UNSHARP_AMOUNT: float = 1.5
    ENHANCEMENT_UNSHARP_RADIUS: int = 3
    ENHANCEMENT_BILATERAL_D: int = 7
    ENHANCEMENT_BILATERAL_SIGMA: int = 55
    ENHANCEMENT_CLAHE_CLIP: float = 2.0

    # ---------------- EXIF + Color Dominante ----------------
    ENABLE_EXIF_GPS: bool = True
    ENABLE_COLOR_ANALYSIS: bool = True
    COLOR_KMEANS_K: int = 4
    COLOR_MIN_CLUSTER_RATIO: float = 0.08    # ignora clusters pequeños
    COLOR_DELTAE_THRESHOLD: float = 18.0     # tolerancia DeltaE LAB
    COLOR_FRAUD_RATIO: float = 0.65          # si >65% de fotos no coinciden => fraude
    COLOR_REGISTERED_FIELD: str = "color"    # campo en documento vehículo (ej: vehicles_col)
    COLOR_FRAUD_POLICY: str = "FLAG"         # FLAG | ABORT | REVIEW
    COLOR_NAME_NORMALIZE: bool = True        # normalizar nombres predefinidos

    # ---------------- Otras extensiones potenciales ----------------
    ENABLE_PART_COMPLETENESS_SCORE: bool = True
    PART_COMPLETENESS_MIN_RATIO: float = 0.6

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()