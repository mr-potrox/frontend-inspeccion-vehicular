from typing import Optional, Dict, Any, Tuple, List
from PIL import Image, ExifTags
import io
import numpy as np
import cv2
from ..config import settings
from math import sqrt

# Map de colores básicos (RGB)
BASE_COLOR_NAMES = {
    "white": (240,240,240),
    "black": (20,20,20),
    "silver": (192,192,192),
    "gray": (128,128,128),
    "red": (180,20,20),
    "maroon": (110,15,15),
    "blue": (25,60,170),
    "navy": (15,30,80),
    "green": (25,140,60),
    "darkgreen": (15,70,35),
    "yellow": (240,220,50),
    "orange": (240,140,30),
    "brown": (90,60,30),
    "beige": (210,200,170),
    "gold": (200,160,30),
    "purple": (110,40,150)
}

def _rgb_to_lab(r,g,b):
    # OpenCV expects BGR
    arr = np.uint8([[[b,g,r]]])
    lab = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB)[0][0]
    return lab

BASE_COLOR_NAMES_LAB = {k: _rgb_to_lab(*v) for k,v in BASE_COLOR_NAMES.items()}

def delta_e_lab(lab1, lab2):
    return sqrt((lab1[0]-lab2[0])**2 + (lab1[1]-lab2[1])**2 + (lab1[2]-lab2[2])**2)

def dominant_color(rgb_bytes: bytes) -> Optional[Dict[str, Any]]:
    if not settings.ENABLE_COLOR_ANALYSIS:
        return None
    try:
        img = Image.open(io.BytesIO(rgb_bytes)).convert("RGB")
    except Exception:
        return None
    arr = np.array(img)
    if arr.size == 0:
        return None
    # Downsample
    h, w = arr.shape[:2]
    factor = max(1, int(min(h,w)/300))
    small = arr[::factor, ::factor, :]
    data = small.reshape(-1,3).astype(np.float32)

    # kmeans
    K = max(2, settings.COLOR_KMEANS_K)
    criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 25, 1.0)
    _ret, labels, centers = cv2.kmeans(data, K, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
    labels = labels.flatten()
    counts = np.bincount(labels)
    total = counts.sum()

    # Seleccionar cluster dominante (descartando clusters minúsculos)
    ratios = counts / total
    order = np.argsort(ratios)[::-1]
    for idx in order:
        if ratios[idx] < settings.COLOR_MIN_CLUSTER_RATIO:
            continue
        c = centers[idx]
        r,g,b = [int(v) for v in c.tolist()]
        name, delta = _closest_color_name(r,g,b)
        return {
            "rgb": [r,g,b],
            "name": name,
            "delta_to_named": delta,
            "ratio": float(ratios[idx]),
            "k": K
        }
    return None

def _closest_color_name(r,g,b) -> Tuple[str, float]:
    target_lab = _rgb_to_lab(r,g,b)
    best = None
    best_d = 1e9
    for name, lab in BASE_COLOR_NAMES_LAB.items():
        d = delta_e_lab(target_lab, lab)
        if d < best_d:
            best_d = d
            best = name
    return best, best_d

def extract_exif_gps(img_bytes: bytes) -> Optional[Dict[str, float]]:
    if not settings.ENABLE_EXIF_GPS:
        return None
    try:
        img = Image.open(io.BytesIO(img_bytes))
        exif = img._getexif()
        if not exif:
            return None
        tag_map = {ExifTags.TAGS.get(k): v for k,v in exif.items() if k in ExifTags.TAGS}
        gps = tag_map.get("GPSInfo")
        if not gps:
            return None
        gps_parsed = {}
        for t,v in gps.items():
            name = ExifTags.GPSTAGS.get(t)
            gps_parsed[name] = v
        lat = _convert_gps_coord(gps_parsed.get("GPSLatitude"), gps_parsed.get("GPSLatitudeRef"))
        lon = _convert_gps_coord(gps_parsed.get("GPSLongitude"), gps_parsed.get("GPSLongitudeRef"))
        if lat is None or lon is None:
            return None
        return {"lat": lat, "lon": lon}
    except Exception:
        return None

def _convert_gps_coord(value, ref) -> Optional[float]:
    if not value or not ref:
        return None
    try:
        d = value[0][0]/value[0][1]
        m = value[1][0]/value[1][1]
        s = value[2][0]/value[2][1]
        coord = d + (m/60.0) + (s/3600.0)
        if ref in ['S','W']:
            coord = -coord
        return coord
    except Exception:
        return None

def majority_color_fraud(registered_color: str, detected: List[Dict[str,Any]]) -> Dict[str, Any]:
    """
    Compara lista de detecciones de color (cada una con name).
    Retorna dict con summary y flags.
    """
    if not detected:
        return {"fraud": False, "reason": "no_colors", "mismatch_ratio": 0.0}
    reg = (registered_color or "").strip().lower()
    if not reg:
        return {"fraud": False, "reason": "no_registered", "mismatch_ratio": 0.0}

    mismatches = 0
    total = 0
    for c in detected:
        n = (c.get("name") or "").lower()
        if not n:
            continue
        total += 1
        # Simple equivalencia: si deltaE > threshold o nombre distinto => mismatch
        if n != reg:
            mismatches += 1
    if total == 0:
        return {"fraud": False, "reason": "no_valid_colors", "mismatch_ratio": 0.0}

    ratio = mismatches / total
    fraud = ratio >= settings.COLOR_FRAUD_RATIO
    return {
        "fraud": fraud,
        "reason": "color_mismatch" if fraud else "ok",
        "mismatch_ratio": ratio,
        "registered": reg,
        "total": total
    }