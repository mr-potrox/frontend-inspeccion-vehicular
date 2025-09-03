import cv2
import numpy as np

def check_quality(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return False
    h, w = img.shape[:2]
    if w < 600 or h < 400:
        return False
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 50:
        return False
    return True