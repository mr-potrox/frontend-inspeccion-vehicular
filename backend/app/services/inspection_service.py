import datetime, uuid
from statistics import mode
from typing import Dict, Any, List, Tuple
from ..database import inspections_col
from ..utils.exif_geo import geo_stats
from ..config import settings

def _aggregate_colors(colors: List[str])->Dict[str,Any]:
    c=[x for x in colors if x]
    if not c: return {"consensus":None,"all":[]}
    try: consensus=mode(c)
    except: consensus=c[0]
    return {"consensus": consensus, "all": c}

def _compute_verdict(damage_n:int, missing_n:int, color_match: bool)->Dict[str,Any]:
    cond=[]
    if damage_n>15 or missing_n>2: verdict="REJECT"
    elif damage_n>5 or missing_n>0 or not color_match:
        verdict="REVIEW"
        if damage_n>5: cond.append("Peritaje adicional (muchos daños).")
        if missing_n>0: cond.append("Reponer partes faltantes.")
        if not color_match: cond.append("Verificar color en registro.")
    else: verdict="APPROVE"
    score=max(0.05, 1.0-0.03*damage_n-0.1*missing_n-(0 if color_match else 0.1))
    return {"verdict":verdict,"conditions":cond,"score":round(score,3)}

def evaluate_geolocation(points: List[Tuple[float,float]]):
    stats=geo_stats(points)
    status="OK"; flags=[]
    if stats["count"]<=1:
        status="INSUFFICIENT"
    else:
        if stats["max_dist"]>settings.GEO_HARD_DISTANCE:
            status="FAIL"; flags.append("GEO_HARD_MISMATCH")
        elif stats["max_dist"]>settings.GEO_WARN_DISTANCE:
            status="WARN"; flags.append("GEO_INCONSISTENT")
    return {"status":status,"stats":stats,"flags":flags}

def save_inspection(plate, damage, parts_presence, missing_parts,
                    conf_d, conf_p, colors_info, verdict_block,
                    session_id, notes, geo_block, fraud_flags, review_flags, status):
    doc={
        "inspection_id": str(uuid.uuid4()),
        "session_id": session_id,
        "plate": plate.upper(),
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "damage_detections": damage,
        "parts_presence": parts_presence,
        "missing_parts": missing_parts,
        "thresholds": {"damage": conf_d, "parts": conf_p},
        "colors": colors_info,
        "verdict": verdict_block if status.startswith("COMPLETED") else None,
        "notes": notes,
        "geo": geo_block,
        "fraud_flags": fraud_flags,
        "review_flags": review_flags,
        "status": status,
        "model_version": settings.MODEL_VERSION,
        "model_sha": settings.MODEL_SHA
    }
    inspections_col.insert_one(doc)
    doc.pop("_id",None)
    return doc

def build_markdown_report(inspection: Dict[str,Any])->str:
    dmg=len(inspection.get("damage_detections",[]))
    miss=len(inspection.get("missing_parts",[]))
    colors=inspection.get("colors",{})
    geo=inspection.get("geo",{})
    lines=[
        "# Reporte de Inspección Vehicular",
        f"- ID: {inspection['inspection_id']}",
        f"- Placa: {inspection['plate']}",
        f"- Fecha: {inspection['timestamp']}",
        f"- Modelo YOLO: {inspection.get('model_version')} ({inspection.get('model_sha')})",
        "",
        "## Resumen",
        f"- Daños: {dmg}",
        f"- Partes faltantes: {miss}",
        f"- Color consenso: {colors.get('consensus')}",
        f"- Estado: {inspection['status']}",
    ]
    if inspection.get("verdict"):
        lines.append(f"- Veredicto: {inspection['verdict']['verdict']} (score {inspection['verdict']['score']})")
    if inspection.get("review_flags"):
        lines.append(f"- Flags revisión: {', '.join(inspection['review_flags'])}")
    if inspection.get("fraud_flags"):
        lines.append(f"- Flags fraude: {', '.join(inspection['fraud_flags'])}")
    lines += ["", "## Geolocalización"]
    if geo:
        lines.append(f"- Estado geo: {geo.get('status')} | max_dist={geo.get('stats',{}).get('max_dist','?')} m")
    lines += ["", "## Daños"]
    for d in inspection.get("damage_detections",[]):
        lines.append(f"- {d['label']} (conf {d['confidence']:.2f}) box={d['box']}")
    lines += ["", "## Partes"]
    for p,info in inspection.get("parts_presence",{}).items():
        est="OK" if info["present"] else "FALTA"
        lines.append(f"- {p}: {est} (conf {info['confidence']:.2f})")
    lines += ["", "## Notas"]
    notes=inspection.get("notes",[])
    if notes:
        for n in notes: lines.append(f"- {n}")
    else:
        lines.append("- (sin notas)")
    return "\n".join(lines)