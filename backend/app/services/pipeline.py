from typing import Dict, Any, List
import cv2
import numpy as np
from ..config import settings
from ..yolo_model import infer_damage, infer_parts
from .image_preprocess import enhance_for_damage, classical_scratch_candidates, nms_merge
from .color_exif import dominant_color, extract_exif_gps

async def run_full_pipeline(
    session_id: str,
    plate: str,
    img_bytes: bytes,
    conf_damage: float | None,
    conf_parts: float | None,
    note: str | None,
    browser_lat: float | None,
    browser_lon: float | None
) -> Dict[str, Any]:
    cd = conf_damage or settings.DEFAULT_CONF_DAMAGE
    cp = conf_parts or settings.DEFAULT_CONF_PARTS
    color_info = dominant_color(img_bytes)
    exif_gps = extract_exif_gps(img_bytes)

    # Convert base to RGB numpy
    rgb = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    if rgb is None:
        return {
            "damage": [],
            "parts_presence": {},
            "missing_parts": [],
            "color_detected": color_info,
            "color_match": False,
            "exif_geo": exif_gps
        }
    rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)

    # Inferencia primaria (original)
    damage_primary = infer_damage(img_bytes, cd)

    # Preprocesamiento y segunda pasada
    damage_enhanced = []
    if settings.ENABLE_IMAGE_ENHANCEMENT and settings.ENABLE_DUAL_PASS_DAMAGE:
        enhanced = enhance_for_damage(rgb)
        # Re-encode a bytes para pasar al modelo
        _, buf = cv2.imencode(".jpg", cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR))
        damage_enhanced = infer_damage(buf.tobytes(), cd)

    all_damage = damage_primary + damage_enhanced

    # Candidatos clásicos scratch
    classical_boxes = []
    if settings.ENABLE_CLASSICAL_SCRATCH:
        cb = classical_scratch_candidates(rgb)
        for box in cb:
            classical_boxes.append({
                "label": "scratch",
                "confidence": settings.CLASSICAL_FAKE_CONF,
                "box": box,
                "_classical": True
            })

    if classical_boxes:
        all_damage = nms_merge(all_damage, classical_boxes, settings.MERGE_IOU_THRESHOLD)
    else:
        # Asegurar sin duplicados excesivos
        all_damage = nms_merge(all_damage, [], settings.MERGE_IOU_THRESHOLD)

    parts_presence = infer_parts(img_bytes, cp)
    missing_parts = [k for k,v in parts_presence.items() if not v.get("present")]

    return {
        "damage": all_damage,
        "parts_presence": parts_presence,
        "missing_parts": missing_parts,
        "color_detected": {"color_name": None},
        "color_match": False,
        "exif_geo": None
    }