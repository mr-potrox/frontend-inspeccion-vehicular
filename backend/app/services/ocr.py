import re
import io
from typing import List, Dict, Any
from PIL import Image
import numpy as np
from ..config import settings

try:
    import easyocr
except Exception:
    easyocr = None

_reader = None

def _get_reader():
    global _reader
    if _reader is None and settings.ENABLE_OCR and easyocr:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader

def _clean(txt: str) -> str:
    return re.sub(r'[^A-Z0-9]', '', txt.upper())

def ocr_text(img_bytes: bytes) -> List[Dict[str,Any]]:
    if not settings.ENABLE_OCR:
        return []
    rd = _get_reader()
    if not rd:
        return []
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return []
    res = rd.readtext(np.array(img))  # type: ignore
    out = []
    for box, text, conf in res:
        out.append({
            "text_raw": text,
            "text": _clean(text),
            "conf": float(conf),
            "box": box
        })
    out.sort(key=lambda x: x["conf"], reverse=True)
    return out[:settings.OCR_MAX_RESULTS]

def extract_plate_candidates(results):
    pat = re.compile(settings.OCR_PLATE_REGEX)
    return [r for r in results if pat.match(r["text"])]

def extract_vin_candidates(results):
    pat = re.compile(settings.OCR_VIN_REGEX)
    out = []
    for r in results:
        t = r["text"]
        if 11 <= len(t) <= 17 and pat.match(t):
            out.append(r)
    return out