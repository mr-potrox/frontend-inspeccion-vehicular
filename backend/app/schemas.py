from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class DamageBox(BaseModel):
    label: str
    confidence: float
    box: List[float]

class PartPresence(BaseModel):
    present: bool
    confidence: float
    box: Optional[List[float]] = None

class ScratchCandidate(BaseModel):
    box: List[int]
    aspect: Optional[float] = None

class ScratchInfo(BaseModel):
    count: int
    scratch_candidates: List[ScratchCandidate] = []

class AnalyzeResponse(BaseModel):
    session_id: str
    damage: List[DamageBox]
    parts_presence: Dict[str, PartPresence]
    missing_parts: List[str]
    color_detected: Dict[str, Any]
    color_match: bool
    exif_geo: Optional[List[float]] = None
    fraud_flags: List[str]
    review_flags: List[str] = []
    aborted: bool
    abort_reason: Optional[str] = None
    images_in_session: int
    preproc_metrics: Dict[str, Any]
    scratch: ScratchInfo
    quality_status: str
    debug_images: Dict[str, str] | None = None

class FinalizeResponse(BaseModel):
    inspection_id: Optional[str]
    session_id: str
    plate: Optional[str]
    damage_detections: List[DamageBox] = []
    parts_presence: Dict[str, PartPresence] = {}
    missing_parts: List[str] = []
    colors: Dict[str, Any] | None = None
    verdict: Dict[str, Any] | None = None
    vehicle_color_db: Optional[str]
    color_match: Optional[bool]
    fraud_flags: List[str] = []
    review_flags: List[str] = []
    status: str
    report_markdown: Optional[str]
    aborted: Optional[bool]
    abort_reason: Optional[str] = None
    vehicle: Dict[str, Any] | None = None
    driver: Dict[str, Any] | None = None
    geo: Any | None = None
    identity_validated: bool | None = None
    identity_payload: Dict[str, Any] | None = None
    vehicle_history: Dict[str, Any] | None = None

class ReportResponse(BaseModel):
    inspection_id: str
    report_markdown: str

class IdentityVerifyRequest(BaseModel):
    name: str
    document: str

class IdentityVerifyResponse(BaseModel):
    valid: bool
    matched_driver: Dict[str, Any] | None = None

class VehicleHistoryResponse(BaseModel):
    plate: str
    infractions: int
    previous_owners: int
    tech_ok: bool
    notes: List[str] = []