import io
import os
from typing import List, Dict, Any
from functools import lru_cache
from PIL import Image
from ultralytics import YOLO
import numpy as np
from .config import settings
from .services.label_provider import get_label_sets

def _log(event: str, **kw):
    # Ajusta a tu logger real
    print(f"[yolo_model] {event} {kw}")

DAMAGE_MODEL_PATH = settings.DAMAGE_MODEL_PATH
PARTS_MODEL_PATH = settings.PARTS_MODEL_PATH

# Normalización manual de partes a claves consistentes
PART_NORMALIZATION = {
    "bonet": "bonnet",
    "bonnet": "bonnet",
    "bumper": "bumper",
    "door": "door",
    "headlight": "headlight",
    "mirror": "mirror",
    "tailight": "taillight",
    "taillight": "taillight",
    "windshield": "windshield"
}

class ModelBundle:
    def __init__(self, damage: YOLO | None, parts: YOLO | None):
        self.damage = damage
        self.parts = parts

def _safe_load(path: str) -> YOLO | None:
    if not path or not os.path.exists(path):
        _log("model_missing", path=path)
        return None
    try:
        _log("model_load_start", path=path)
        model = YOLO(path)
        _log("model_load_ok", path=path)
        return model
    except Exception as e:
        _log("model_load_error", path=path, error=str(e))
        return None

@lru_cache
def load_models() -> ModelBundle:
    return ModelBundle(
        _safe_load(DAMAGE_MODEL_PATH),
        _safe_load(PARTS_MODEL_PATH)
    )

def warm_models():
    load_models()

def _read_image(img_bytes: bytes) -> Image.Image | None:
    try:
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return None

def _infer_yolo(model: YOLO | None, pil_img: Image.Image, conf: float):
    if model is None:
        return []
    try:
        res = model.predict(pil_img, conf=conf, verbose=False)
    except Exception as e:
        _log("inference_error", error=str(e))
        return []
    if not res:
        return []
    r0 = res[0]
    names_map = getattr(r0, "names", {}) or getattr(model, "names", {}) or {}
    out = []
    for b in r0.boxes:
        try:
            xyxy = b.xyxy[0].tolist()
            cls_id = int(b.cls[0])
            conf_v = float(b.conf[0])
            lab = names_map.get(cls_id, str(cls_id))
            x1,y1,x2,y2 = [int(v) for v in xyxy]
            out.append({
                "label": lab,
                "confidence": conf_v,
                "box": [x1,y1,x2,y2]
            })
        except Exception:
            continue
    return out

def infer_damage(img_bytes: bytes, conf: float) -> List[Dict[str, Any]]:
    pil = _read_image(img_bytes)
    if pil is None:
        return []
    dets = _infer_yolo(load_models().damage, pil, conf)
    # Filtrar por lista esperada (settings.DAMAGE_LABELS)
    allowed = set(get_label_sets()["damage_labels"])
    return [d for d in dets if d["label"] in allowed]

def _normalize_part_label(lbl: str) -> str:
    k = lbl.lower().strip()
    return PART_NORMALIZATION.get(k, k)

def infer_parts(img_bytes: bytes, conf: float) -> Dict[str, Dict[str, Any]]:
    pil = _read_image(img_bytes)
    label_sets = get_label_sets()
    expected = label_sets["part_labels"]
    norm_expected = [_normalize_part_label(e) for e in expected]

    presence: Dict[str, Dict[str, Any]] = {
        ne: {"present": False, "confidence": 0.0, "box": None} for ne in norm_expected
    }
    if pil is None:
        return presence

    raw = _infer_yolo(load_models().parts, pil, conf)
    best = {}
    for d in raw:
        norm = _normalize_part_label(d["label"])
        if norm not in best or d["confidence"] > best[norm]["confidence"]:
            best[norm] = {
                "present": True,
                "confidence": d["confidence"],
                "box": d["box"]
            }
    # Merge
    for k,v in best.items():
        presence[k] = v
    return presence

def _ensure():
    warm_models()