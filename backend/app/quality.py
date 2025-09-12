import cv2
import numpy as np
from typing import Dict, Any, Tuple

MIN_WIDTH = 450
MIN_HEIGHT = 300

# Estos umbrales se exponen vía /health para el frontend (dinámicos)
MIN_BLUR_VAR = 60.0          # debajo => blur
MIN_BLUR_VAR_WARN = 80.0     # warn (opcional para UI)
VERY_LOW_BLUR_VAR = 40.0     # debajo => very_blur (forzar recaptura)

def enhance_and_denoise(img: np.ndarray) -> np.ndarray:
    f1 = cv2.bilateralFilter(img, 7, 50, 50)
    f2 = cv2.medianBlur(f1, 3)
    lab = cv2.cvtColor(f2, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    lab2 = cv2.merge([l2, a, b])
    out = cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)
    return out

def compute_edge_density(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 80, 160)
    return float((edges > 0).sum()) / (gray.shape[0] * gray.shape[1])

def detect_scratches(img: np.ndarray) -> Dict[str, Any]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    grad = cv2.Laplacian(blur, cv2.CV_64F)
    g = cv2.convertScaleAbs(grad)
    th = cv2.adaptiveThreshold(
        g, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 15, 5
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
    morph = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cand = []
    h, w = gray.shape
    for c in contours:
        x, y, wc, hc = cv2.boundingRect(c)
        area = wc * hc
        if area < 30:
            continue
        aspect = max(wc, hc) / (min(wc, hc) + 1e-3)
        if aspect < 3:
            continue
        if wc < 6 and hc < 6:
            continue
        if wc > 0.5 * w or hc > 0.5 * h:
            continue
        cand.append({
            "box": [int(x), int(y), int(x + wc), int(y + hc)],
            "aspect": round(aspect, 2)
        })
    return {"count": len(cand), "scratch_candidates": cand}

def build_overlay(img: np.ndarray, scratches: Dict[str, Any]) -> np.ndarray:
    overlay = img.copy()
    for sc in scratches.get("scratch_candidates", []):
        x1, y1, x2, y2 = sc["box"]
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 50, 50), 2)
    return overlay

def assess_extended(image_bytes: bytes, want_debug=False) -> Dict[str, Any]:
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"ok": False, "reason": "decode_failed"}

    h, w = img.shape[:2]
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        return {"ok": False, "reason": "too_small", "w": w, "h": h}

    denoised = enhance_and_denoise(img)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    blur_var = float(lap.var())
    edge_d = compute_edge_density(gray)
    mean_int = float(gray.mean())
    std_int = float(gray.std())

    status = "ok"
    if blur_var < VERY_LOW_BLUR_VAR:
        status = "very_blur"
    elif blur_var < MIN_BLUR_VAR:
        status = "blur"
    elif blur_var < MIN_BLUR_VAR_WARN:
        status = "warn"

    scratches = detect_scratches(denoised)

    debug_images = {}
    if want_debug:
        try:
            overlay = build_overlay(denoised, scratches)
            debug_images["overlay_b64"] = _to_b64(overlay)
            debug_images["processed_b64"] = _to_b64(denoised)
        except Exception:
            pass

    return {
        "ok": status == "ok" or status == "warn",
        "quality_status": status,
        "blur_var": round(blur_var, 2),
        "edge_density": round(edge_d, 4),
        "mean": round(mean_int, 1),
        "contrast": round(std_int, 1),
        "scratches": scratches,
        "debug_images": debug_images
    }

def _to_b64(img: np.ndarray) -> str:
    import base64
    _, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return base64.b64encode(buf).decode("utf-8")