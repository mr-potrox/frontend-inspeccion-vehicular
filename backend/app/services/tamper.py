import io, os, cv2, numpy as np, piexif
from PIL import Image, ImageChops
from functools import lru_cache
from ..config import settings

@lru_cache
def _load_tamper_model():
    if not settings.ENABLE_TAMPER_DETECTION:
        return None
    path = settings.TAMPER_CNN_MODEL_PATH
    if not os.path.isfile(path):
        return None
    try:
        net = cv2.dnn.readNetFromONNX(path)
        return net
    except Exception:
        return None

def _ela_image(img: Image.Image, quality: int):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    buf.seek(0)
    recompressed = Image.open(buf)
    ela = ImageChops.difference(img, recompressed)
    extrema = ela.getextrema()
    max_diff = max(ex[1] for ex in extrema)
    scale = 255.0 / max(1, max_diff)
    ela = ela.point(lambda p: p * scale)
    return ela

def _cnn_score(rgb):
    net = _load_tamper_model()
    if net is None:
        return None
    size = 224
    inp = cv2.resize(rgb, (size,size))
    blob = cv2.dnn.blobFromImage(inp, 1/255.0, (size,size), swapRB=True, crop=False)
    net.setInput(blob)
    out = net.forward().squeeze()
    if out.ndim == 0:
        return float(out)
    if out.shape[0] == 2:
        ex = np.exp(out - out.max())
        prob = ex / ex.sum()
        return float(prob[1])
    return float(out.mean())

def _exif_analyze(pil: Image.Image):
    flags = []
    try:
        exif_dict = piexif.load(pil.info.get("exif", b""))
    except Exception:
        return {"flags": ["EXIF_MISSING_ALL"]}
    expected = [k.strip() for k in settings.TAMPER_EXIF_MISSING_KEYS.split(",")]
    present_keys = []
    for ifd in exif_dict:
        if isinstance(exif_dict[ifd], dict):
            present_keys.extend(exif_dict[ifd].keys())
    if not present_keys:
        flags.append("EXIF_EMPTY")
    soft = None
    try:
        soft = exif_dict["0th"].get(piexif.ImageIFD.Software)
        if soft:
            soft = soft.decode(errors="ignore").lower()
    except Exception:
        pass
    if soft:
        for suspect in settings.TAMPER_EXIF_SOFTWARE_SUSPECT.split(","):
            if suspect.strip() and suspect.strip().lower() in soft:
                flags.append("EXIF_SOFTWARE_EDIT")
                break
    for ek in expected:
        if ek == "DateTimeOriginal":
            try:
                dto = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
                if not dto:
                    flags.append("MISSING_DateTimeOriginal")
            except Exception:
                flags.append("MISSING_DateTimeOriginal")
    return {"flags": flags or []}

def analyze_tamper(img_bytes: bytes):
    if not settings.ENABLE_TAMPER_DETECTION:
        return None
    try:
        pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return {"status": "error", "reason": "unreadable"}
    ela = _ela_image(pil, settings.TAMPER_ELA_JPEG_QUALITY)
    arr = np.array(ela)
    mean_diff = float(arr.mean())
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    h,w = gray.shape
    block_vals = []
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            sub = gray[y:y+8, x:x+8]
            if sub.size < 64: continue
            block_vals.append(sub.mean())
    block_vals = np.array(block_vals)
    block_std = float(block_vals.std()) if block_vals.size else 0.0
    rgb = np.array(pil)
    cnn_score = _cnn_score(rgb)
    exif_report = _exif_analyze(pil)
    suspect_reasons = []
    if mean_diff > settings.TAMPER_ELA_MEAN_THRESHOLD and block_std > settings.TAMPER_BLOCK_DIFF_THRESHOLD:
        suspect_reasons.append("ELA_PATTERN")
    if cnn_score is not None and cnn_score >= settings.TAMPER_CNN_THRESHOLD:
        suspect_reasons.append("CNN_SCORE")
    if any(f for f in exif_report["flags"] if "MISSING_" in f or f == "EXIF_SOFTWARE_EDIT"):
        suspect_reasons.append("EXIF_FLAGS")
    return {
        "mean_diff": mean_diff,
        "block_std": block_std,
        "cnn_score": cnn_score,
        "exif_flags": exif_report["flags"],
        "suspect": len(suspect_reasons) > 0,
        "reasons": suspect_reasons
    }