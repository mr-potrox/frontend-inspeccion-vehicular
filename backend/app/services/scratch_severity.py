import os, cv2, numpy as np
from functools import lru_cache
from ..config import settings

@lru_cache
def _load_scratch_model():
    if not settings.ENABLE_SCRATCH_SEVERITY:
        return None
    if not os.path.isfile(settings.SCRATCH_SEVERITY_MODEL_PATH):
        return None
    try:
        net = cv2.dnn.readNetFromONNX(settings.SCRATCH_SEVERITY_MODEL_PATH)
        return net
    except Exception:
        return None

def classify_scratch_severity(rgb, box):
    x1,y1,x2,y2 = [int(v) for v in box]
    h,w = rgb.shape[:2]
    x1=max(0,x1);y1=max(0,y1);x2=min(w,x2);y2=min(h,y2)
    patch = rgb[y1:y2, x1:x2]
    labels = [l.strip() for l in settings.SCRATCH_SEV_LABELS.split(",")]
    net = _load_scratch_model()
    if net is not None and patch.size:
        size = 160
        inp = cv2.resize(patch, (size,size))
        blob = cv2.dnn.blobFromImage(inp, 1/255.0, (size,size), swapRB=True, crop=False)
        net.setInput(blob)
        out = net.forward().squeeze()
        exp = np.exp(out - out.max())
        prob = exp / exp.sum()
        idx = int(prob.argmax())
        label = labels[idx] if idx < len(labels) else "moderate"
        return {
            "severity": label,
            "score": float(prob[idx]),
            "method": "model"
        }
    length = max(abs(x2-x1), abs(y2-y1))
    if length < settings.SCRATCH_SEV_FALLBACK_EDGELEN_MINOR:
        sev = "minor"
    elif length >= settings.SCRATCH_SEV_FALLBACK_EDGELEN_SEVERE:
        sev = "severe"
    else:
        sev = "moderate"
    return {
        "severity": sev,
        "score": 0.5,
        "method": "heuristic",
        "est_length": length
    }