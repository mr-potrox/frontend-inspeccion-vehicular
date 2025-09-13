import os, cv2, numpy as np
from functools import lru_cache
from ..config import settings

@lru_cache
def _load_bg_model():
    if not settings.ENABLE_BG_CLASSIFIER:
        return None
    if not os.path.isfile(settings.BG_CLASSIFIER_MODEL_PATH):
        return None
    try:
        net = cv2.dnn.readNetFromONNX(settings.BG_CLASSIFIER_MODEL_PATH)
        return net
    except Exception:
        return None

def classify_background(rgb):
    if not settings.ENABLE_BG_CLASSIFIER:
        return None
    net = _load_bg_model()
    if net is None:
        arr = rgb.astype(np.float32)
        var = float(arr.var())
        label = "outdoor" if var > 900 else "indoor"
        return {"label": label, "score": 0.50, "accepted": True, "model": False}
    size = settings.BG_CLASSIFIER_INPUT
    inp = cv2.resize(rgb, (size,size))
    blob = cv2.dnn.blobFromImage(inp, 1/255.0, (size,size), swapRB=True, crop=False)
    net.setInput(blob)
    out = net.forward().squeeze()
    exp = np.exp(out - out.max())
    prob = exp / exp.sum()
    labels = [l.strip() for l in settings.BG_LABELS.split(",")]
    idx = int(prob.argmax())
    label = labels[idx] if idx < len(labels) else "unknown"
    score = float(prob[idx])
    outdoor_group = [s.strip() for s in settings.BG_OUTDOOR_GROUP.split(",")]
    accepted = score >= settings.BG_MIN_ACCEPT_SCORE
    return {
        "label": label,
        "score": score,
        "accepted": accepted,
        "model": True,
        "probs": {labels[i]: float(prob[i]) for i in range(min(len(labels), len(prob)))},
        "is_outdoor_group": label in outdoor_group
    }