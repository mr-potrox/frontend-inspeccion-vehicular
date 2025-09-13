import cv2, numpy as np, os
from functools import lru_cache
from ..config import settings

@lru_cache
def _load_onnx():
    if not settings.SEG_USE_MODEL:
        return None
    if not os.path.isfile(settings.SEG_MODEL_PATH):
        return None
    try:
        net = cv2.dnn.readNetFromONNX(settings.SEG_MODEL_PATH)
        return net
    except Exception:
        return None

def _infer_model(rgb: np.ndarray):
    net = _load_onnx()
    if net is None:
        return None
    h, w = rgb.shape[:2]
    inp = cv2.dnn.blobFromImage(rgb, 1/255.0, (512,512), swapRB=True, crop=False)
    net.setInput(inp)
    out = net.forward()
    m = out
    if m.ndim == 4 and m.shape[1] > 1:
        m = m[:,1:2]
    m = m.squeeze()
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    prob = 1 / (1 + np.exp(-m))
    mask = (prob >= settings.SEG_THRESHOLD).astype(np.uint8) * 255
    return mask

def vehicle_mask(rgb: np.ndarray):
    if not settings.ENABLE_SEGMENTATION:
        return None, 0.0
    mask = _infer_model(rgb)
    if mask is None:
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        mask1 = cv2.inRange(hsv, (0,0,30), (180,60,255))
        mask2 = cv2.inRange(hsv, (0,0,0), (180,25,200))
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.medianBlur(mask, 5)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((11,11), np.uint8))
        cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return None, 0.0
        areas = [cv2.contourArea(c) for c in cnts]
        idx = int(np.argmax(areas))
        big = np.zeros_like(mask)
        cv2.drawContours(big, [cnts[idx]], -1, 255, -1)
        area_ratio = areas[idx] / (mask.shape[0]*mask.shape[1] + 1e-6)
        if area_ratio < settings.SEG_MIN_VEHICLE_AREA_RATIO:
            return None, area_ratio
        return big, float(area_ratio)
    coverage = float((mask>0).sum() / (mask.shape[0]*mask.shape[1] + 1e-6))
    if coverage < settings.SEG_MIN_VEHICLE_AREA_RATIO:
        return None, coverage
    return mask, coverage

def filter_detections_by_mask(dets, mask: np.ndarray):
    if mask is None or not dets:
        return dets
    keep = []
    for d in dets:
        x1,y1,x2,y2 = d["box"]
        x1 = max(int(x1),0); y1=max(int(y1),0)
        x2 = int(x2); y2=int(y2)
        sub = mask[y1:y2, x1:x2]
        if sub.size == 0:
            continue
        ratio = (sub>0).sum() / sub.size
        if ratio >= settings.SEG_BOX_MIN_INTERSECTION:
            keep.append(d)
    return keep