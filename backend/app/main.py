import imghdr
import magic
from typing import Optional, List, Dict, Any
from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException,
    WebSocket, WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_client import Counter, Histogram
from anyio import from_thread

from .config import settings
from .logging_utils import setup_logging, log_event
from .schemas import (
    AnalyzeResponse, FinalizeResponse, ReportResponse,
    IdentityVerifyRequest, IdentityVerifyResponse, VehicleHistoryResponse
)
from .services.label_provider import get_label_sets
from .services.pipeline import run_full_pipeline
from .services.color_exif import majority_color_fraud
from .services.pdf_export import build_full_pdf
from .services.markdown_builder import build_markdown_report
from .services.verdict import compute_verdict as _compute_verdict
from .services.geo import evaluate_geolocation
from .services.vehicle_service import get_or_create_vehicle, get_vehicle
from .services.driver_service import get_random_driver
from .yolo_model import _ensure as warmup_models
from .repositories.session_repository import SessionRepository
from .database import (
    vehicles_col, inspections_col, sessions_col,
    drivers_col
)
from .websocket_manager import manager

setup_logging(settings.LOG_LEVEL)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.API_TITLE)

REQUESTS = Counter("api_requests_total", "Total API requests", ["endpoint", "method", "status"])
ANALYZE_LAT = Histogram("inspection_analyze_seconds", "Analyze endpoint latency")
FINALIZE_LAT = Histogram("inspection_finalize_seconds", "Finalize endpoint latency")

session_repo = SessionRepository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.API_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"]
)

# ---------------- Helpers ----------------
def _metrics(ep: str, method: str, status: int):
    REQUESTS.labels(ep, method, status).inc()

def _validate_upload(file: UploadFile) -> bytes:
    raw = file.file.read()
    file.file.seek(0)
    if len(raw) > settings.MAX_IMAGE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")
    mime = magic.from_buffer(raw, mime=True) if magic else None
    if mime and not mime.startswith("image/"):
        raise HTTPException(status_code=400, detail="Formato no permitido")
    fmt = imghdr.what(None, raw)
    if fmt is None or fmt == "svg":
        raise HTTPException(status_code=400, detail="Imagen inválida")
    return raw

# --------------- Startup -----------------
@app.on_event("startup")
async def startup():
    warmup_models()
    log_event("startup_complete")

# --------------- Health ------------------
@app.get("/health")
def health():
    labels = get_label_sets()
    return {
        "status": "ok",
        "model_version": settings.MODEL_VERSION,
        "models": {
            "damage": {
                "name": settings.DAMAGE_MODEL_NAME,
                "path": settings.DAMAGE_MODEL_PATH,
                "default_conf": settings.DEFAULT_CONF_DAMAGE
            },
            "parts": {
                "name": settings.PARTS_MODEL_NAME,
                "path": settings.PARTS_MODEL_PATH,
                "default_conf": settings.DEFAULT_CONF_PARTS
            }
        },
        "labels": labels,
        "features": {
            "segmentation": settings.ENABLE_SEGMENTATION,
            "ocr": settings.ENABLE_OCR,
            "illumination": settings.ENABLE_ILLUMINATION_ANALYSIS,
            "background_classifier": settings.ENABLE_BG_CLASSIFIER,
            "scratch_severity": getattr(settings, "ENABLE_SCRATCH_SEVERITY", False),
            "tamper": settings.ENABLE_TAMPER_DETECTION,
            "part_completeness": settings.ENABLE_PART_COMPLETENESS_SCORE
        },
        "pdf_enabled": settings.ENABLE_PDF_EXPORT
    }

# --------------- Identity ----------------
@app.post("/identity/verify", response_model=IdentityVerifyResponse)
def identity_verify(payload: IdentityVerifyRequest):
    doc = drivers_col.find_one({"document": payload.document})
    if not doc:
        return IdentityVerifyResponse(valid=False, matched_driver=None)
    name_ok = payload.name.strip().lower() in (
        (doc.get("name") or "").lower(),
        (doc.get("full_name") or "").lower()
    )
    return IdentityVerifyResponse(valid=name_ok, matched_driver=doc if name_ok else None)

# --------------- Vehicle history ---------
@app.get("/vehicle/history", response_model=VehicleHistoryResponse)
def vehicle_history(plate: str):
    v = vehicles_col.find_one({"plate": plate})
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    hist = v.get("history", {})
    return VehicleHistoryResponse(
        plate=plate,
        infractions=hist.get("infractions", 0),
        previous_owners=hist.get("previous_owners", 1),
        tech_ok=hist.get("tech_ok", True),
        notes=hist.get("notes", [])
    )

# --------------- Vehicle verify ----------
@app.get("/inspection/verify")
def inspection_verify(plate: str):
    v = get_vehicle(plate)
    if not v:
        return {"found": False, "msg": "Vehículo no encontrado"}
    return {"found": True, "data": v}

# --------------- Analyze ------------------
@app.post("/inspection/analyze", response_model=AnalyzeResponse)
@limiter.limit(settings.RATE_LIMIT)
async def inspection_analyze(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    plate: str = Form(...),
    photo_key: str = Form(...),
    conf_damage: float = Form(None),
    conf_parts: float = Form(None),
    note: str = Form(None),
    browser_lat: float = Form(None),
    browser_lon: float = Form(None),
    debug: int = Form(0)
):
    log_event("analyze_in", session_id=session_id, plate=plate, photo_key=photo_key)
    raw = _validate_upload(file)
    want_debug = bool(debug)

    # Calidad
    from .quality import assess_extended
    quality = assess_extended(raw, want_debug=want_debug)

    review_flags: List[str] = []
    if quality["quality_status"] in ("blur", "very_blur"):
        review_flags.append("LOW_SHARPNESS")
    if quality["scratches"]["count"] > 0:
        review_flags.append("SCRATCH_CANDIDATES")

    with ANALYZE_LAT.time():
        pipeline = await run_full_pipeline(
            session_id=session_id,
            plate=plate,
            photo_key=photo_key,
            img_bytes=raw,
            conf_damage=conf_damage,
            conf_parts=conf_parts,
            note=note,
            browser_lat=browser_lat,
            browser_lon=browser_lon
        )

    # Política de fondo
    bg_policy = (pipeline.get("background") or {}).get("policy")
    if bg_policy and bg_policy.get("inconsistent"):
        review_flags.append("BACKGROUND_POLICY")

    result = {
        "session_id": session_id,
        "photo_key": photo_key,
        "damage": pipeline["damage"],
        "parts_presence": pipeline["parts_presence"],
        "missing_parts": pipeline["missing_parts"],
        "color_detected": pipeline["color_detected"],
        "color_match": pipeline["color_match"],
        "exif_geo": pipeline.get("exif_geo"),
        "segmentation": pipeline.get("segmentation"),
        "illumination": pipeline.get("illumination"),
        "background": pipeline.get("background"),
        "ocr": pipeline.get("ocr"),
        "tamper": pipeline.get("tamper"),
        "fraud_flags": [],
        "review_flags": review_flags,
        "aborted": False,
        "abort_reason": None,
        "images_in_session": session_repo.count_images(session_id) + 1,
        "preproc_metrics": {
            "lap_var": quality.get("blur_var"),
            "edge_density": quality.get("edge_density"),
            "mean_gray": quality.get("mean"),
            "contrast": quality.get("contrast")
        },
        "scratch": quality["scratches"],
        "quality_status": quality["quality_status"],
        "debug_images": quality.get("debug_images") if want_debug else None
    }

    # Tamper sospechoso
    tamper_block = pipeline.get("tamper")
    if tamper_block and tamper_block.get("suspect"):
        result["fraud_flags"].append("TAMPER_SUSPECT")

    session_repo.store_image_analysis(session_id, plate, result, raw)
    if note:
        session_repo.add_note(session_id, note)

    log_event("analyze_out",
              session_id=session_id,
              photo_key=photo_key,
              quality_status=quality["quality_status"],
              scratches=quality["scratches"]["count"])
    _metrics("/inspection/analyze", "POST", 200)
    return result

# --------------- Finalize -----------------
@app.post("/inspection/finalize", response_model=FinalizeResponse)
@limiter.limit(settings.RATE_LIMIT)
def inspection_finalize(
    session_id: str = Form(...),
    plate: str = Form(...),
    conf_damage: float = Form(None),
    conf_parts: float = Form(None),
    clear: bool = Form(True)
):
    log_event("finalize_in", session_id=session_id, plate=plate)
    with FINALIZE_LAT.time():
        images = session_repo.list_images(session_id)
        if not images:
            raise HTTPException(status_code=400, detail="Sesión vacía")

        aborted, abort_reason = session_repo.is_aborted(session_id)
        vehicle = get_or_create_vehicle(plate)
        driver = get_random_driver()

        all_damage: List[Dict[str,Any]] = []
        all_colors: List[Dict[str,Any]] = []
        parts_union: Dict[str, Dict[str,Any]] = {}
        exif_points = []
        illum_list = []
        bg_list = []
        ocr_plate_matches = []
        ocr_vin_candidates = []
        tamper_suspects = 0

        for im in images:
            an = im.get("analysis", {})
            all_damage.extend(an.get("damage", []))

            for p, info in (an.get("parts_presence") or {}).items():
                cur = parts_union.get(p, {"present": False, "confidence": 0.0, "box": None})
                if info["confidence"] > cur["confidence"]:
                    parts_union[p] = info

            if an.get("color_detected"):
                all_colors.append(an["color_detected"])
            if an.get("exif_geo"):
                exif_points.append(an["exif_geo"])
            if an.get("illumination"):
                illum_list.append(an["illumination"])
            if an.get("background"):
                bg_list.append(an["background"])

            ocr_block = (an.get("ocr") or {})
            ocr_plate_matches.extend(ocr_block.get("plate_candidates") or [])
            ocr_vin_candidates.extend(ocr_block.get("vin_candidates") or [])

            tamper_block = an.get("tamper")
            if tamper_block and tamper_block.get("suspect"):
                tamper_suspects += 1

        missing = [p for p, i in parts_union.items() if not i["present"]]

        registered_color = (vehicle.get("color") or "").lower()
        color_eval = majority_color_fraud(registered_color, all_colors) if registered_color else {
            "fraud": False, "reason": "no_registered", "mismatch_ratio": 0.0
        }

        geo_block = evaluate_geolocation(exif_points)
        fraud_flags = list(set(session_repo.list_flags(session_id) + geo_block.get("flags", [])))
        review_flags = session_repo.list_review_flags(session_id)

        if color_eval.get("fraud"):
            fraud_flags.append("COLOR_FRAUD")
            if settings.COLOR_FRAUD_POLICY == "ABORT":
                aborted = True
                abort_reason = "COLOR_FRAUD"
            elif settings.COLOR_FRAUD_POLICY == "REVIEW":
                review_flags.append("COLOR_REVIEW")

        vin_detected = ocr_vin_candidates[0]["text"] if ocr_vin_candidates else None
        if ocr_plate_matches:
            best_plate = ocr_plate_matches[0].get("text")
            if best_plate and best_plate != plate:
                fraud_flags.append("PLATE_OCR_MISMATCH")

        if tamper_suspects > 0:
            fraud_flags.append("TAMPER_SUSPECT")

        status = "COMPLETED"
        verdict_block = None
        if aborted:
            status = f"ABORTED_{abort_reason}"
            fraud_flags.append(abort_reason)
        elif geo_block["status"] == "FAIL":
            status = "FAILED_GEO_MISMATCH"
            fraud_flags.append("INSPECTION_ABORTED_GEO")
        else:
            verdict_block = _compute_verdict(len(all_damage), len(missing), not color_eval.get("fraud"))

        notes = session_repo.list_notes(session_id)
        identity_payload = session_repo.get_identity(session_id)
        vehicle_history = session_repo.get_vehicle_history(session_id)
        identity_validated = bool(identity_payload and identity_payload.get("valid"))

        completeness_score = None
        if settings.ENABLE_PART_COMPLETENESS_SCORE and parts_union:
            present = sum(1 for v in parts_union.values() if v["present"])
            completeness_score = round(present / max(1, len(parts_union)), 3)

        doc = {
            "inspection_id": session_id,
            "session_id": session_id,
            "plate": plate,
            "damage_detections": all_damage,
            "parts_presence": parts_union,
            "missing_parts": missing,
            "color_evaluation": color_eval,
            "vehicle_color_db": vehicle.get("color"),
            "fraud_flags": list(set(fraud_flags)),
            "review_flags": list(set(review_flags)),
            "status": status,
            "aborted": aborted,
            "abort_reason": abort_reason,
            "verdict": verdict_block,
            "vehicle": vehicle,
            "driver": driver,
            "notes": notes,
            "identity_validated": identity_validated,
            "identity_payload": identity_payload,
            "vehicle_history": vehicle_history,
            "geo_summary": geo_block,
            "part_completeness_score": completeness_score,
            "illumination_frames": illum_list,
            "background_frames": bg_list,
            "tamper_suspects": tamper_suspects,
            "ocr_summary": {
                "plate_candidates": ocr_plate_matches[:5],
                "vin_candidates": ocr_vin_candidates[:5],
                "vin_detected": vin_detected
            }
        }

        doc["report_markdown"] = build_markdown_report(doc)
        inspections_col.replace_one({"inspection_id": session_id}, doc, upsert=True)

        if clear:
            session_repo.clear_session(session_id)

        async def _notify():
            await manager.broadcast(session_id, {
                "event": "finalize:done",
                "session_id": session_id,
                "status": status,
                "aborted": aborted
            })

        from_thread.run(_notify)
        log_event("finalize_out", session_id=session_id, status=status)
        _metrics("/inspection/finalize", "POST", 200)
        return doc

# --------------- Report PDF ---------------
@app.get("/inspection/report/{inspection_id}", response_model=ReportResponse)
def get_report_pdf(inspection_id: str):
    if not settings.ENABLE_PDF_EXPORT:
        raise HTTPException(status_code=403, detail="PDF export deshabilitado")

    doc = inspections_col.find_one({"inspection_id": inspection_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")

    if not doc.get("report_markdown"):
        doc["report_markdown"] = build_markdown_report(doc)

    pdf_bytes = build_full_pdf(doc)
    filename = f"reporte_{inspection_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# --------------- Root ---------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "inspection-api"}

# --------------- WebSocket ----------------
@app.websocket("/ws/inspection/{session_id}")
async def ws_inspection(session_id: str, websocket: WebSocket):
    await manager.connect(session_id, websocket)
    try:
        await manager.broadcast(session_id, {"event": "ws:connected", "session_id": session_id})
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(session_id, websocket)