import numpy as np
from ..config import settings

def illumination_summary(gray):
    if not settings.ENABLE_ILLUMINATION_ANALYSIS:
        return None
    mean = float(gray.mean())
    p5 = float(np.percentile(gray, 5))
    p95 = float(np.percentile(gray, 95))
    dyn = p95 - p5
    status = "ok"
    flags = []
    if mean < settings.ILLUM_DARK_MEAN:
        status = "dark"; flags.append("LOW_LIGHT")
    elif mean > settings.ILLUM_BRIGHT_MEAN:
        status = "bright"; flags.append("OVER_EXPOSED")
    if dyn < settings.ILLUM_LOW_DR_RANGE:
        flags.append("LOW_DYNAMIC_RANGE")
        if status == "ok":
            status = "flat"
    return {
        "mean": mean,
        "p5": p5,
        "p95": p95,
        "dynamic_range": dyn,
        "status": status,
        "flags": flags
    }