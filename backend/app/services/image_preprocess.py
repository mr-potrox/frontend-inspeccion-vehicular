import cv2
import numpy as np
from ..config import settings

def enhance_for_damage(rgb: np.ndarray) -> np.ndarray:
    """
    Aplica pipeline de realce para resaltar rayones/delaminaciones:
    - Bilateral (suaviza conservando bordes)
    - Unsharp mask
    - CLAHE canal L
    - Top-hat morfológico para resaltar líneas claras
    """
    img = rgb.copy()

    if settings.ENHANCEMENT_BILATERAL_D > 0:
        img = cv2.bilateralFilter(
            img,
            d=settings.ENHANCEMENT_BILATERAL_D,
            sigmaColor=settings.ENHANCEMENT_BILATERAL_SIGMA,
            sigmaSpace=settings.ENHANCEMENT_BILATERAL_SIGMA
        )

    # Unsharp
    blur = cv2.GaussianBlur(img, (settings.ENHANCEMENT_UNSHARP_RADIUS*2+1,)*2, 0)
    unsharp = cv2.addWeighted(img, settings.ENHANCEMENT_UNSHARP_AMOUNT, blur, - (settings.ENHANCEMENT_UNSHARP_AMOUNT - 1), 0)

    # CLAHE en L
    lab = cv2.cvtColor(unsharp, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=settings.ENHANCEMENT_CLAHE_CLIP, tileGridSize=(8,8))
    l2 = clahe.apply(l)
    lab2 = cv2.merge([l2, a, b])
    clahe_rgb = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB)

    # Top-hat
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    tophat = cv2.morphologyEx(clahe_rgb, cv2.MORPH_TOPHAT, kernel)
    # Mezcla suave original + tophat
    mix = cv2.addWeighted(clahe_rgb, 0.85, tophat, 0.35, 0)
    return mix

def classical_scratch_candidates(rgb: np.ndarray):
    """
    Detecta candidatos a rayones finos mediante:
    - Conversión a gris
    - Realce (clahe + blur)
    - Canny
    - Dilatación ligera
    - Filtrado por aspecto y tamaño
    Retorna lista de cajas [x1,y1,x2,y2]
    """
    if not settings.ENABLE_CLASSICAL_SCRATCH:
        return []

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8,8)).apply(gray)
    blur = cv2.GaussianBlur(clahe, (3,3), 0)
    edges = cv2.Canny(blur, 50, 140)
    dil = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in contours:
        if len(c) < 12:
            continue
        x,y,w,h = cv2.boundingRect(c)
        if h < 2 and w < 2:
            continue
        # Longitud mínima
        if max(w,h) < settings.CLASSICAL_SCRATCH_MIN_LEN:
            continue
        # Rayones delgados
        if min(w,h) > settings.CLASSICAL_SCRATCH_MAX_WIDTH:
            continue
        aspect = max(w,h) / (min(w,h)+1e-6)
        if aspect < 2.5:  # suficientemente alargado
            continue
        boxes.append([x,y,x+w,y+h])
        if len(boxes) >= settings.CLASSICAL_SCRATCH_MAX:
            break
    return boxes

def nms_merge(detections, extra, iou_thr: float):
    """
    detections: lista dict {label, confidence, box}
    extra: misma estructura
    NMS simple por IoU (solo entre combinados).
    """
    all_det = detections + extra
    if not all_det:
        return []
    boxes = np.array([d["box"] for d in all_det], dtype=np.float32)
    scores = np.array([d["confidence"] for d in all_det], dtype=np.float32)

    idxs = np.argsort(scores)[::-1]
    keep = []
    while len(idxs):
        i = idxs[0]
        keep.append(i)
        if len(idxs) == 1:
            break
        i_box = boxes[i]
        rest = boxes[idxs[1:]]
        # IoU
        xx1 = np.maximum(i_box[0], rest[:,0])
        yy1 = np.maximum(i_box[1], rest[:,1])
        xx2 = np.minimum(i_box[2], rest[:,2])
        yy2 = np.minimum(i_box[3], rest[:,3])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w*h
        area_i = (i_box[2]-i_box[0])*(i_box[3]-i_box[1])
        area_r = (rest[:,2]-rest[:,0])*(rest[:,3]-rest[:,1])
        iou = inter / (area_i + area_r - inter + 1e-6)
        idxs = idxs[1:][iou <= iou_thr]
    return [all_det[i] for i in keep]