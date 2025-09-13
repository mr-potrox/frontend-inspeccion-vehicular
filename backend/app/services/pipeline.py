from typing import Dict, Any
import cv2, numpy as np
from ..config import settings
from ..yolo_model import infer_damage, infer_parts
from .image_preprocess import enhance_for_damage, nms_merge
from .color_exif import dominant_color, extract_exif_gps
from .segmentation import vehicle_mask, filter_detections_by_mask
from .background_classifier import classify_background
from .illumination import illumination_summary
from .ocr import ocr_text, extract_plate_candidates, extract_vin_candidates
from .tamper import analyze_tamper
from .scratch_severity import classify_scratch_severity

OCR_ALLOWED_PHOTOS = {"front", "rear", "vin"}

def _background_policy(photo_key: str, bg_cls: dict | None):
    if not bg_cls:
        return None
    expect_keys = [k.strip() for k in settings.BG_EXPECT_OUTDOOR_KEYS.split(",")]
    outdoor_group = [s.strip() for s in settings.BG_OUTDOOR_GROUP.split(",")]
    if settings.BG_POLICY_EXPECT_OUTDOOR and photo_key in expect_keys:
        if bg_cls.get("label") not in outdoor_group:
            return {"inconsistent": True, "expected": "outdoor"}
    return {"inconsistent": False}

async def run_full_pipeline(
    session_id: str,
    plate: str,
    photo_key: str,
    img_bytes: bytes,
    conf_damage: float | None,
    conf_parts: float | None,
    note: str | None,
    browser_lat: float | None,
    browser_lon: float | None
) -> Dict[str, Any]:
    cd = conf_damage or settings.DEFAULT_CONF_DAMAGE
    cp = conf_parts or settings.DEFAULT_CONF_PARTS
    bgr = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        return {
            "damage": [],
            "parts_presence": {},
            "missing_parts": [],
            "color_detected": None,
            "color_match": False,
            "exif_geo": None
        }
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    seg_mask, seg_cov = vehicle_mask(rgb)
    damage_primary = infer_damage(img_bytes, cd)
    damage_enhanced = []
    if settings.ENABLE_IMAGE_ENHANCEMENT and settings.ENABLE_DUAL_PASS_DAMAGE:
        enhanced = enhance_for_damage(rgb)
        _, buf = cv2.imencode(".jpg", cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR))
        damage_enhanced = infer_damage(buf.tobytes(), cd)
    all_damage = nms_merge(damage_primary + damage_enhanced, [], settings.MERGE_IOU_THRESHOLD)
    if seg_mask is not None:
        all_damage = filter_detections_by_mask(all_damage, seg_mask)
    if settings.ENABLE_SCRATCH_SEVERITY:
        for d in all_damage:
            if d.get("label") == "scratch":
                d["scratch_severity"] = classify_scratch_severity(rgb, d["box"])
    parts_presence = infer_parts(img_bytes, cp)
    missing_parts = [k for k,v in parts_presence.items() if not v.get("present")]
    color_info = dominant_color(img_bytes)
    exif_gps = extract_exif_gps(img_bytes)
    illum = illumination_summary(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
    bg_cls = classify_background(rgb)
    bg_policy = _background_policy(photo_key, bg_cls)
    ocr_results = []
    plate_candidates = []
    vin_candidates = []
    if photo_key in OCR_ALLOWED_PHOTOS:
        ocr_results = ocr_text(img_bytes)
        plate_candidates = extract_plate_candidates(ocr_results)
        vin_candidates = extract_vin_candidates(ocr_results)
    tamper = analyze_tamper(img_bytes)
    return {
        "damage": all_damage,
        "parts_presence": parts_presence,
        "missing_parts": missing_parts,
        "color_detected": color_info,
        "color_match": False,
        "exif_geo": exif_gps,
        "segmentation": {
            "mask_available": seg_mask is not None,
            "coverage_ratio": seg_cov
        },
        "illumination": illum,
        "background": {**(bg_cls or {}), "policy": bg_policy} if bg_cls else None,
        "ocr": {
            "raw": ocr_results,
            "plate_candidates": plate_candidates,
            "vin_candidates": vin_candidates
        },
        "tamper": tamper
    }