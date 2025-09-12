import cv2, numpy as np
from typing import Dict, Any, Tuple

_BASE_COLORS = {
    "Blanco": (240,240,240),
    "Negro": (20,20,20),
    "Gris": (128,128,128),
    "Plata": (185,185,185),
    "Rojo": (180,40,40),
    "Azul": (40,70,160),
    "Verde": (40,150,70),
    "Amarillo": (230,210,60),
    "Beige": (205,190,150),
    "Naranja": (210,110,40)
}

def _closest(rgb: Tuple[int,int,int]) -> str:
    r,g,b = rgb
    best,bd=None,1e12
    for name,(R,G,B) in _BASE_COLORS.items():
        d=(r-R)**2+(g-G)**2+(b-B)**2
        if d<bd: bd=d; best=name
    return best

def detect_dominant_color(image_bytes: bytes, k=3) -> Dict[str, Any]:
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"color_name": None, "rgb": None}
    h,w = img.shape[:2]
    scale = 320/max(h,w)
    if scale<1:
        img = cv2.resize(img,(int(w*scale),int(h*scale)))
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    Z = lab.reshape((-1,3)).astype(np.float32)
    K = min(k, len(Z))
    criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,20,1.0)
    _ret,label,center = cv2.kmeans(Z,K,None,criteria,3,cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(label.flatten())
    dom_lab = center[np.argmax(counts)]
    dom_lab_img = np.uint8([[dom_lab]])
    dom_bgr = cv2.cvtColor(dom_lab_img, cv2.COLOR_Lab2BGR)[0][0]
    b,g,r = map(int, dom_bgr)
    rgb=(r,g,b)
    return {"color_name": _closest(rgb), "rgb": rgb}